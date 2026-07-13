import Foundation

private let learningRepo = "/tmp/kit-learning-repo"
private let learningIdentity = LearningPayloadValidator.sidecarRepoIdentity(selectedRepo: learningRepo)
private let learningSidecarRoot = LearningPayloadValidator.expectedSidecarStateDirectory(selectedRepo: learningRepo)
private let eventID = "evt-0123456789abcdef0123"
private let proposalID = "prop-0123456789abcdef0123"
private let decisionID = "dec-0123456789abcdef0123"

func runLearningChecks() throws {
    try checkLaunchParsing()
    try checkExactLearningBuilders()
    try checkLearningValidatorRejections()
    try checkPrivateTmpSidecarCompatibility()
    try checkLearningPayloadDecodingAndMetadata()
    try checkLearningRunnerCancellation()
    try checkLearningWriteQueueCancellation()
}

private func checkLearningRunnerCancellation() throws {
    let fileManager = FileManager.default
    let tempDir = fileManager.temporaryDirectory.appendingPathComponent("KitCompanionLearningCancellation-\(UUID().uuidString)", isDirectory: true)
    defer { try? fileManager.removeItem(at: tempDir) }
    try fileManager.createDirectory(at: tempDir, withIntermediateDirectories: true)

    let fakeKit = tempDir.appendingPathComponent("sleeping-kit")
    try """
    #!/usr/bin/env python3
    import hashlib
    import json
    import os
    import pathlib
    import sys
    import time

    repo = next(arg.split("=", 1)[1] for arg in sys.argv if arg.startswith("--repo="))
    root = str(pathlib.Path(repo).resolve())
    digest = hashlib.sha256(root.encode()).hexdigest()
    base = pathlib.Path(os.environ.get("XDG_STATE_HOME", pathlib.Path.home() / ".local" / "state")).resolve() / "repo-contract-kit"
    slug = __import__("re").sub(r"[^A-Za-z0-9._-]+", "-", pathlib.Path(root).name).strip(".-") or "repo"
    time.sleep(5)
    print(json.dumps({
      "schema_version": 1,
      "command": "learn status",
      "repo": repo,
      "policy_state": "active",
      "policy": {"state": "active", "path": repo + "/.agent-workflows/learning-policy.json", "ownership": "target", "enabled": True, "policy_id": "supervised-learning", "schema_version": 1},
      "learning_paths": {"policy": repo + "/.agent-workflows/learning-policy.json", "schemas": {}, "sidecar": {"root": str(base / (slug + "-" + digest[:16]) / "learning")}},
      "safe_next_commands": [],
      "write_guarantees": {"target_repo_writes": False, "sidecar_writes": False, "global_tool_writes": False, "note": "read only"},
      "target_repo_writes": {"performed": False, "paths": [], "reason": "read only"},
      "sidecar_writes": {"performed": False, "paths": [], "reason": "read only"},
      "global_writes": {"performed": False, "paths": [], "reason": "read only"},
      "sidecar_state": {"repo_state_dir": str(base / (slug + "-" + digest[:16])), "repo": {"root": root, "hash": digest, "id": digest[:16]}},
      "exit_code": 0
    }))
    """.write(to: fakeKit, atomically: true, encoding: .utf8)
    try fileManager.setAttributes([.posixPermissions: 0o755], ofItemAtPath: fakeKit.path)

    let command = try LearningCommandBuilder.status(repo: tempDir.path)
    let semaphore = DispatchSemaphore(value: 0)
    var result: Result<LearningStatusPayload, Error>?
    let task = Task {
        do {
            result = .success(try await LearningRunner().run(
                LearningStatusPayload.self,
                command: command,
                selectedRepo: tempDir.path,
                kitPath: fakeKit.path
            ))
        } catch {
            result = .failure(error)
        }
        semaphore.signal()
    }

    Thread.sleep(forTimeInterval: 0.15)
    let cancellationStarted = Date()
    task.cancel()
    if semaphore.wait(timeout: .now() + 2) == .timedOut {
        throw CheckFailure.failed("canceled learning runner should complete without waiting for the fake kit sleep")
    }
    try check(Date().timeIntervalSince(cancellationStarted) < 2, "canceled learning runner should complete within the bounded timeout")
    switch result {
    case .failure(_ as CancellationError):
        break
    case .failure(let error):
        throw CheckFailure.failed("canceled learning runner should throw CancellationError, got: \(error)")
    case .success:
        throw CheckFailure.failed("canceled learning runner should not return a payload")
    case .none:
        throw CheckFailure.failed("canceled learning runner did not report a result")
    }
}

private func checkLearningWriteQueueCancellation() throws {
    let fileManager = FileManager.default
    let tempDir = fileManager.temporaryDirectory.appendingPathComponent("KitCompanionLearningQueue-\(UUID().uuidString)", isDirectory: true)
    defer { try? fileManager.removeItem(at: tempDir) }
    try fileManager.createDirectory(at: tempDir, withIntermediateDirectories: true)

    let fakeKit = tempDir.appendingPathComponent("serializing-kit")
    try """
    #!/usr/bin/env python3
    import pathlib
    import sys
    import time

    repo = next(arg.split("=", 1)[1] for arg in sys.argv if arg.startswith("--repo="))
    summary = next(arg.split("=", 1)[1] for arg in sys.argv if arg.startswith("--summary="))
    pathlib.Path(repo, "started-" + summary).write_text("started")
    time.sleep(5 if summary == "waiter" else 0.4)
    print("{}")
    raise SystemExit(1)
    """.write(to: fakeKit, atomically: true, encoding: .utf8)
    try fileManager.setAttributes([.posixPermissions: 0o755], ofItemAtPath: fakeKit.path)

    func command(summary: String) throws -> LearningCommand {
        try LearningCommandBuilder.eventRecord(
            repo: tempDir.path,
            kind: .validation,
            summary: summary,
            evidence: ["test"],
            outcome: .confirmed,
            source: .human,
            privacyLabel: .internal,
            approved: true
        )
    }
    func launch(_ command: LearningCommand, signal semaphore: DispatchSemaphore) {
        Task {
            do {
                _ = try await LearningRunner().run(
                    LearningEventRecordPayload.self,
                    command: command,
                    selectedRepo: tempDir.path,
                    kitPath: fakeKit.path
                )
            } catch {
            }
            semaphore.signal()
        }
    }

    let firstDone = DispatchSemaphore(value: 0)
    launch(try command(summary: "first"), signal: firstDone)
    let firstStarted = tempDir.appendingPathComponent("started-first")
    let startDeadline = Date().addingTimeInterval(1)
    while !fileManager.fileExists(atPath: firstStarted.path), Date() < startDeadline {
        Thread.sleep(forTimeInterval: 0.01)
    }
    try check(fileManager.fileExists(atPath: firstStarted.path), "first write should start before queueing a waiter")

    let waiterDone = DispatchSemaphore(value: 0)
    var waiterError: Error?
    let waiterCommand = try command(summary: "waiter")
    let waiterTask = Task {
        do {
            _ = try await LearningRunner().run(
                LearningEventRecordPayload.self,
                command: waiterCommand,
                selectedRepo: tempDir.path,
                kitPath: fakeKit.path
            )
        } catch {
            waiterError = error
        }
        waiterDone.signal()
    }
    Thread.sleep(forTimeInterval: 0.1)
    waiterTask.cancel()
    if waiterDone.wait(timeout: .now() + 1) == .timedOut {
        throw CheckFailure.failed("canceled same-repo write waiter should leave the serializer queue promptly")
    }
    try check(waiterError is CancellationError, "canceled queued write should throw CancellationError")

    let thirdDone = DispatchSemaphore(value: 0)
    launch(try command(summary: "third"), signal: thirdDone)
    if thirdDone.wait(timeout: .now() + 2) == .timedOut {
        throw CheckFailure.failed("canceled queued write must not run and block a later same-repo write")
    }
    _ = firstDone.wait(timeout: .now() + 1)
}

private func checkLaunchParsing() throws {
    let parsed = KitCompanionLaunchOptions.parse(
        arguments: ["/Applications/KitCompanion.app/Contents/MacOS/KitCompanion", "--open-dashboard", "learning"]
    )
    try check(parsed?.dashboardSection == .learning, "cold launch should accept the exact learning dashboard route")
    try check(DashboardSection.allCases.count == 5, "learning should be the fifth dashboard section")

    let rejected: [[String]] = [
        ["KitCompanion"],
        ["KitCompanion", "--open-dashboard"],
        ["KitCompanion", "--open-dashboard", "unknown"],
        ["KitCompanion", "--open-dashboard", "learning", "--json"],
        ["KitCompanion", "learn", "status"],
        ["KitCompanion", "--open-dashboard=learning"]
    ]
    for arguments in rejected {
        try check(KitCompanionLaunchOptions.parse(arguments: arguments) == nil, "malformed launch route should fail closed: \(arguments)")
    }
}

private func checkExactLearningBuilders() throws {
    let status = try LearningCommandBuilder.status(repo: learningRepo)
    try check(
        status.arguments == ["learn", "status", "--repo=\(learningRepo)", "--json"],
        "status builder should be exact"
    )

    let eventList = try LearningCommandBuilder.eventList(repo: learningRepo, limit: 25)
    try check(
        eventList.arguments == ["learn", "event", "list", "--repo=\(learningRepo)", "--limit=25", "--json"],
        "event list builder should bound and render its limit"
    )

    let eventRecord = try LearningCommandBuilder.eventRecord(
        repo: learningRepo,
        kind: .validation,
        summary: "Validated the bounded workflow.",
        evidence: ["Focused check passed", "Manual review passed"],
        outcome: .confirmed,
        source: .human,
        privacyLabel: .internal,
        approved: true
    )
    try check(
        eventRecord.arguments == [
            "learn", "event", "record", "--repo=\(learningRepo)",
            "--kind=validation", "--summary=Validated the bounded workflow.",
            "--evidence=Focused check passed", "--evidence=Manual review passed",
            "--outcome=confirmed", "--source=human", "--privacy-label=internal",
            "--approved", "--approval-state=approved", "--json"
        ],
        "event record builder should preserve supported repeated evidence only"
    )

    let proposalCreate = try LearningCommandBuilder.proposalCreate(
        repo: learningRepo,
        title: "Tighten checks",
        classification: .harness,
        scopes: ["macos/KitCompanion", "Makefile"],
        recommendedChange: "Add bounded validation.",
        evidenceEventIDs: [eventID],
        privacyLabel: .internal
    )
    try check(
        proposalCreate.arguments == [
            "learn", "proposal", "create", "--repo=\(learningRepo)",
            "--title=Tighten checks", "--classification=harness",
            "--scope=macos/KitCompanion", "--scope=Makefile",
            "--recommended-change=Add bounded validation.",
            "--evidence-event=\(eventID)", "--privacy-label=internal", "--json"
        ],
        "proposal builder should render exact repeatable scope and lineage flags"
    )

    let decisionRecord = try LearningCommandBuilder.decisionRecord(
        repo: learningRepo,
        proposalID: proposalID,
        outcome: .approved,
        decider: "Repository owner",
        rationale: "The bounded evidence is sufficient.",
        followUp: ["Revalidate after release"],
        humanReviewConfirmed: true
    )
    try check(
        decisionRecord.arguments == [
            "learn", "decision", "record", "--repo=\(learningRepo)",
            "--proposal-id=\(proposalID)", "--outcome=approved",
            "--decider=Repository owner", "--rationale=The bounded evidence is sufficient.",
            "--follow-up=Revalidate after release", "--human-review-confirmed", "--json"
        ],
        "decision builder should require the explicit human-review flag"
    )

    let contextBuild = try LearningCommandBuilder.contextBuild(repo: learningRepo, decisionID: decisionID)
    try check(
        contextBuild.arguments == ["learn", "context", "build", "--repo=\(learningRepo)", "--decision-id=\(decisionID)", "--json"],
        "context builder should be exact"
    )

    let threadSummaryImport = try LearningCommandBuilder.threadSummaryImport(
        repo: learningRepo,
        inputPath: "/tmp/redacted-summary.json",
        approved: true
    )
    try check(
        threadSummaryImport.arguments == ["learn", "thread-summary", "import", "--repo=\(learningRepo)", "--input=/tmp/redacted-summary.json", "--approved", "--json"],
        "thread-summary builder should require an absolute input and approval"
    )

    let upstreamExport = try LearningCommandBuilder.upstreamExport(
        repo: learningRepo,
        decisionID: decisionID,
        privacyLabel: .internal,
        redactionConfirmed: true
    )
    try check(
        upstreamExport.arguments == [
            "learn", "upstream", "export", "--repo=\(learningRepo)",
            "--decision-id=\(decisionID)", "--privacy-label=internal",
            "--redaction-confirmed", "--json"
        ],
        "upstream export builder should use the source-review privacy and redaction gates"
    )

    for command in [
        try LearningCommandBuilder.proposalList(repo: learningRepo, limit: 1),
        try LearningCommandBuilder.decisionList(repo: learningRepo, limit: 50),
        try LearningCommandBuilder.contextList(repo: learningRepo, limit: 50),
        try LearningCommandBuilder.threadSummaryList(repo: learningRepo, limit: 50),
        try LearningCommandBuilder.upstreamList(repo: learningRepo, limit: 50),
        try LearningCommandBuilder.upstreamReconcile(repo: learningRepo, limit: 50),
        try LearningCommandBuilder.evaluate(repo: learningRepo)
    ] {
        _ = try LearningCommandValidator.validate(command.arguments, selectedRepo: learningRepo)
    }
}

private func checkLearningValidatorRejections() throws {
    let hostile: [[String]] = [
        ["learn"],
        ["learn", "event"],
        ["learn", "event", "list", "--repo=\(learningRepo)", "--limit=0", "--json"],
        ["learn", "event", "list", "--repo=\(learningRepo)", "--limit=51", "--json"],
        ["learn", "status", "--repo", "relative/repo", "--json"],
        ["learn", "status", "--repo", "/tmp/wrong-repo", "--json"],
        ["learn", "status", "--repo", learningRepo, "--repo", learningRepo, "--json"],
        ["learn", "status", "--repo", learningRepo, "--json", "--json"],
        ["learn", "status", "--repo", learningRepo, "--global", "--json"],
        ["learn", "event", "record", "--repo", learningRepo, "--kind", "validation", "--summary", "x", "--outcome", "confirmed", "--source", "human", "--approved", "--apply", "--json"],
        ["learn", "thread-summary", "import", "--repo", learningRepo, "--input", "relative.json", "--approved", "--json"],
        ["learn", "upstream", "export", "--repo", learningRepo, "--decision-id", decisionID, "--privacy-label", "private-local", "--redaction-confirmed", "--json"],
        ["learn", "upstream", "export", "--repo", learningRepo, "--decision-id", decisionID, "--privacy-label", "internal", "--json"],
        ["status", "--repo", learningRepo, "--json"],
        ["learn-anything", "--repo", learningRepo, "--json"]
    ]
    for arguments in hostile {
        try expectThrows("learning validator should reject hostile arguments: \(arguments)") {
            _ = try LearningCommandValidator.validate(arguments, selectedRepo: learningRepo)
        }
    }

    try expectThrows("generic read-only runner must fail closed for learn") {
        try KitProcessRunner.validateReadOnlyCommand(["learn", "status", "--repo", learningRepo, "--json"])
    }
    try expectThrows("generic write runner must fail closed for learn-prefixed routes") {
        try KitProcessRunner.validateAllowedWriteCommand(["learning", "--repo", learningRepo, "--apply", "--json"])
    }

    try expectThrows("proposal builder must reject a blank title before confirmation") {
        _ = try LearningCommandBuilder.proposalCreate(
            repo: learningRepo, title: " \n\t ", classification: .harness, scopes: ["macos/KitCompanion"],
            recommendedChange: "Add bounded validation.", evidenceEventIDs: [eventID], privacyLabel: .internal
        )
    }
    try expectThrows("proposal builder must reject a blank recommended change before confirmation") {
        _ = try LearningCommandBuilder.proposalCreate(
            repo: learningRepo, title: "Tighten checks", classification: .harness, scopes: ["macos/KitCompanion"],
            recommendedChange: " \n\t ", evidenceEventIDs: [eventID], privacyLabel: .internal
        )
    }
    try expectThrows("decision builder must reject a blank decider before confirmation") {
        _ = try LearningCommandBuilder.decisionRecord(
            repo: learningRepo, proposalID: proposalID, outcome: .approved, decider: " \n\t ",
            rationale: "The bounded evidence is sufficient.", followUp: [], humanReviewConfirmed: true
        )
    }
    try expectThrows("decision builder must reject a blank rationale before confirmation") {
        _ = try LearningCommandBuilder.decisionRecord(
            repo: learningRepo, proposalID: proposalID, outcome: .approved, decider: "Repository owner",
            rationale: " \n\t ", followUp: [], humanReviewConfirmed: true
        )
    }

    for (label, arguments) in [
        ("proposal title", ["learn", "proposal", "create", "--repo=\(learningRepo)", "--title= \t", "--classification=harness", "--scope=macos/KitCompanion", "--recommended-change=Add bounded validation.", "--evidence-event=\(eventID)", "--privacy-label=internal", "--json"]),
        ("proposal recommendation", ["learn", "proposal", "create", "--repo=\(learningRepo)", "--title=Tighten checks", "--classification=harness", "--scope=macos/KitCompanion", "--recommended-change= \n", "--evidence-event=\(eventID)", "--privacy-label=internal", "--json"]),
        ("decision decider", ["learn", "decision", "record", "--repo=\(learningRepo)", "--proposal-id=\(proposalID)", "--outcome=approved", "--decider= \t", "--rationale=Evidence is sufficient.", "--human-review-confirmed", "--json"]),
        ("decision rationale", ["learn", "decision", "record", "--repo=\(learningRepo)", "--proposal-id=\(proposalID)", "--outcome=approved", "--decider=Repository owner", "--rationale= \n", "--human-review-confirmed", "--json"])
    ] {
        try expectThrows("learning validator must reject blank \(label)") {
            _ = try LearningCommandValidator.validate(arguments, selectedRepo: learningRepo)
        }
    }
}

private func checkPrivateTmpSidecarCompatibility() throws {
    let fileManager = FileManager.default
    let repo = "/private/tmp/kit-companion-private-repo"
    let xdgStateHome = "/private/tmp/kit-companion-private-state"
    try fileManager.createDirectory(atPath: repo, withIntermediateDirectories: true)
    try fileManager.createDirectory(atPath: xdgStateHome, withIntermediateDirectories: true)
    defer {
        try? fileManager.removeItem(atPath: repo)
        try? fileManager.removeItem(atPath: xdgStateHome)
    }

    // Python pathlib.Path.resolve() and Darwin realpath both preserve this
    // spelling when /private/tmp is passed explicitly. Foundation does not.
    let expectedHash = "1b27bfa95031442fa74ef7957c90aa7121ea5abe31879574d6c3349a8e8ec462"
    let expectedStateDirectory = "/private/tmp/kit-companion-private-state/repo-contract-kit/kit-companion-private-repo-1b27bfa95031442f"
    let identity = LearningPayloadValidator.sidecarRepoIdentity(selectedRepo: repo)
    let stateDirectory = LearningPayloadValidator.expectedSidecarStateDirectory(
        selectedRepo: repo,
        environment: ["XDG_STATE_HOME": xdgStateHome]
    )
    try check(identity.root == repo, "private temporary repository identity must preserve /private")
    try check(identity.hash == expectedHash && identity.id == "1b27bfa95031442f", "private temporary repository hash must match Python SHA-256 semantics")
    try check(stateDirectory == expectedStateDirectory, "alternate XDG state directory must match the Python CLI spelling exactly")

    let policyPath = repo + "/.agent-workflows/learning-policy.json"
    let payload = LearningStatusPayload(
        schemaVersion: 1,
        command: "learn status",
        repo: repo,
        policyState: "active",
        policy: LearningPolicyStatus(state: "active", path: policyPath, ownership: "target", enabled: true, policyID: "supervised-learning", schemaVersion: 1),
        learningPaths: LearningPaths(policy: policyPath, schemas: [:], sidecar: ["root": stateDirectory + "/learning"]),
        safeNextCommands: [],
        writeGuarantees: LearningWriteGuarantees(targetRepoWrites: false, sidecarWrites: false, globalToolWrites: false, note: "read only"),
        targetRepoWrites: .none,
        sidecarWrites: .none,
        globalWrites: .none,
        sidecarState: LearningSidecarState(repoStateDir: stateDirectory, repo: identity),
        exitCode: 0
    )
    try LearningPayloadValidator.validate(
        payload,
        expectedCommand: .status,
        selectedRepo: repo,
        environment: ["XDG_STATE_HOME": xdgStateHome]
    )
}

private func checkLearningPayloadDecodingAndMetadata() throws {
    try expectThrows("leading-dash free text must be rejected when separated") {
        _ = try LearningCommandValidator.validate(["learn", "event", "record", "--repo=\(learningRepo)", "--kind=validation", "--summary", "-unsafe", "--outcome=confirmed", "--source=human", "--privacy-label=internal", "--approval-state=approved", "--approved", "--json"], selectedRepo: learningRepo)
    }
    let redaction = LearningThreadSummaryInput.Redaction(humanConfirmed: true, rawTranscriptExcluded: true, rawFeedbackExcluded: true, rawEventContentExcluded: true, privateContentExcluded: true)
    func summary(_ id: String = "tsum-01234567890123456789", _ date: String = "2026-07-13T00:00:00Z", _ count: Int = 1) -> LearningThreadSummaryInput {
        LearningThreadSummaryInput(schemaVersion: 1, summaryID: id, reportedAt: date, redaction: redaction, aggregate: .init(interactionCount: count, outcomeCounts: .init(confirmed: count, inconclusive: 0, regressed: 0), classificationCounts: ["documentation": count], redactedSummary: "ok"))
    }
    try expectThrows("nonhex thread summary ID should be rejected") { try summary("tsum-zzzzzzzzzzzzzzzzzzzzz").validate() }
    try expectThrows("non-UTC timestamp should be rejected") { try summary("tsum-01234567890123456789", "2026-07-13T00:00:00+09:30").validate() }
    try expectThrows("negative count should be rejected") { try summary("tsum-01234567890123456789", "2026-07-13T00:00:00Z", -1).validate() }
    try expectThrows("count over 10000 should be rejected") { try summary("tsum-01234567890123456789", "2026-07-13T00:00:00Z", 10_001).validate() }

    let sidecarRoot = learningSidecarRoot
    let statusJSON = """
    {
      "schema_version": 1,
      "command": "learn status",
      "repo": "\(learningRepo)",
      "policy_state": "active",
      "policy": {"state":"active","path":"\(learningRepo)/.agent-workflows/learning-policy.json","ownership":"target","enabled":true,"policy_id":"supervised-learning","schema_version":1},
      "learning_paths": {"policy":"\(learningRepo)/.agent-workflows/learning-policy.json","schemas":{},"sidecar":{"root":"\(sidecarRoot)/learning"}},
      "safe_next_commands": [],
      "write_guarantees": {"target_repo_writes":false,"sidecar_writes":false,"global_tool_writes":false,"note":"read only"},
      "target_repo_writes": {"performed":false,"paths":[],"reason":"read only"},
      "sidecar_writes": {"performed":false,"paths":[],"reason":"read only"},
      "global_writes": {"performed":false,"paths":[],"reason":"read only"},
      "sidecar_state": {"repo_state_dir":"\(sidecarRoot)","repo":{"root":"\(learningIdentity.root)","hash":"\(learningIdentity.hash)","id":"\(learningIdentity.id)"}},
      "exit_code": 0
    }
    """
    let status = try JSONDecoder().decode(LearningStatusPayload.self, from: Data(statusJSON.utf8))
    try check(status.policy.enabled == true, "status payload should decode typed policy state")
    try LearningPayloadValidator.validate(status, expectedCommand: .status, selectedRepo: learningRepo)

    let eventJSON = """
    {
      "schema_version":1,"command":"learn event list","action":"list","repo":"\(learningRepo)",
      "events_path":"\(sidecarRoot)/learning/events","count":1,"warnings":[],
      "events":[{"schema_version":1,"event_id":"\(eventID)","occurred_at":"2026-07-13T00:00:00Z","policy_id":"supervised-learning","repo":"\(learningRepo)","kind":"validation","summary":"A bounded result.","evidence":["check passed"],"outcome":"confirmed","provenance":{"source":"human","capture":"explicit-cli-input"},"privacy_label":"internal","supervision":{"human_approval_required":true,"approval_state":"approved","approval_flag":true}}],
      "target_repo_writes":{"performed":false,"paths":[],"reason":"read only"},
      "sidecar_writes":{"performed":false,"paths":[],"reason":"read only"},
      "global_writes":{"performed":false,"paths":[],"reason":"read only"},
      "sidecar_state":{"repo_state_dir":"\(sidecarRoot)","repo":{"root":"\(learningIdentity.root)","hash":"\(learningIdentity.hash)","id":"\(learningIdentity.id)"}},"exit_code":0
    }
    """
    let events = try JSONDecoder().decode(LearningEventListPayload.self, from: Data(eventJSON.utf8))
    try check(events.events.first?.kind == .validation, "event list should decode typed event values")
    try LearningPayloadValidator.validate(events, expectedCommand: .eventList, selectedRepo: learningRepo)

    func statusWithSidecar(repoStateDir: String, identity: [String: Any]?) throws -> LearningStatusPayload {
        var object = try JSONSerialization.jsonObject(with: Data(statusJSON.utf8)) as! [String: Any]
        var sidecar: [String: Any] = ["repo_state_dir": repoStateDir]
        if let identity { sidecar["repo"] = identity }
        object["sidecar_state"] = sidecar
        return try JSONDecoder().decode(LearningStatusPayload.self, from: JSONSerialization.data(withJSONObject: object))
    }
    let validIdentity: [String: Any] = ["root": learningIdentity.root, "hash": learningIdentity.hash, "id": learningIdentity.id]
    try expectThrows("valid-looking arbitrary sidecar state directories must be rejected") {
        try LearningPayloadValidator.validate(
            try statusWithSidecar(repoStateDir: "/tmp/kit-state/valid-looking", identity: validIdentity),
            expectedCommand: .status,
            selectedRepo: learningRepo
        )
    }
    try expectThrows("sidecar state must include repository identity") {
        _ = try statusWithSidecar(repoStateDir: sidecarRoot, identity: nil)
    }
    for (label, identity) in [
        ("root", ["root": "/tmp/wrong-repo", "hash": learningIdentity.hash, "id": learningIdentity.id]),
        ("hash", ["root": learningIdentity.root, "hash": String(repeating: "0", count: 64), "id": learningIdentity.id]),
        ("id", ["root": learningIdentity.root, "hash": learningIdentity.hash, "id": String(repeating: "0", count: 16)])
    ] {
        try expectThrows("sidecar repository identity with wrong \(label) must be rejected") {
            try LearningPayloadValidator.validate(
                try statusWithSidecar(repoStateDir: sidecarRoot, identity: identity),
                expectedCommand: .status,
                selectedRepo: learningRepo
            )
        }
    }
    let alternateEnvironment = ["XDG_STATE_HOME": "/tmp/kit-learning-alternate-state"]
    let alternateSidecarRoot = LearningPayloadValidator.expectedSidecarStateDirectory(
        selectedRepo: learningRepo,
        environment: alternateEnvironment
    )
    try LearningPayloadValidator.validate(
        try statusWithSidecar(repoStateDir: alternateSidecarRoot, identity: validIdentity),
        expectedCommand: .status,
        selectedRepo: learningRepo,
        environment: alternateEnvironment
    )

    let errorJSON = """
    {"schema_version":1,"command":"learn upstream export","action":"error","repo":"\(learningRepo)","policy_state":"active","policy":{"state":"active"},"learning_paths":{"sidecar":{"root":"\(sidecarRoot)/learning"}},"gate":{"state":"redaction-confirmation-required","reason":"confirm redaction"},"errors":[],"target_repo_writes":{"performed":false,"paths":[],"reason":"blocked"},"sidecar_writes":{"performed":false,"paths":[],"reason":"blocked"},"global_writes":{"performed":false,"paths":[],"reason":"blocked"},"sidecar_state":{"repo_state_dir":"\(sidecarRoot)","repo":{"root":"\(learningIdentity.root)","hash":"\(learningIdentity.hash)","id":"\(learningIdentity.id)"}},"exit_code":1}
    """
    let errorPayload = try JSONDecoder().decode(LearningErrorPayload.self, from: Data(errorJSON.utf8))
    try check(errorPayload.gate?.state == "redaction-confirmation-required", "error payload should decode the exact gate")

    let hostileTargetWrites = status.replacingMetadata(
        targetRepoWrites: LearningWriteMetadata(performed: true, paths: [learningRepo + "/AGENTS.md"], reason: "hostile")
    )
    try expectThrows("target writes must never validate") {
        try LearningPayloadValidator.validate(hostileTargetWrites, expectedCommand: .status, selectedRepo: learningRepo)
    }

    let escapingSidecarWrite = LearningMutationReceipt(
        schemaVersion: 1,
        command: "learn event record",
        action: "record",
        repo: learningRepo,
        targetRepoWrites: .none,
        sidecarWrites: LearningWriteMetadata(performed: true, paths: ["/tmp/outside/event.json"], reason: "hostile"),
        globalWrites: .none,
        sidecarState: LearningSidecarState(repoStateDir: sidecarRoot, repo: learningIdentity),
        exitCode: 0
    )
    try expectThrows("sidecar write paths must remain contained") {
        try LearningPayloadValidator.validate(escapingSidecarWrite, expectedCommand: .eventRecord, selectedRepo: learningRepo)
    }
}
