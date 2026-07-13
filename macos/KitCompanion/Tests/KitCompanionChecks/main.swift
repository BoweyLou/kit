import Foundation
import ServiceManagement

enum CheckFailure: Error, CustomStringConvertible {
    case failed(String)

    var description: String {
        switch self {
        case .failed(let message):
            return message
        }
    }
}

func check(_ condition: @autoclosure () -> Bool, _ message: String) throws {
    if !condition() {
        throw CheckFailure.failed(message)
    }
}

func expectThrows(_ message: String, _ body: () throws -> Void) throws {
    do {
        try body()
    } catch {
        return
    }
    throw CheckFailure.failed(message)
}

final class StreamingTimestampRecorder {
    private let lock = NSLock()
    private var eventAt: Date?
    private var doneAt: Date?

    func recordEventIfNeeded(signal semaphore: DispatchSemaphore) {
        lock.lock()
        if eventAt == nil {
            eventAt = Date()
            semaphore.signal()
        }
        lock.unlock()
    }

    func recordDone() {
        lock.lock()
        doneAt = Date()
        lock.unlock()
    }

    func snapshot() -> (eventAt: Date?, doneAt: Date?) {
        lock.lock()
        defer { lock.unlock() }
        return (eventAt, doneAt)
    }
}

func makeCommand(
    name: String,
    path: [String]? = nil,
    mutation: String = "read-only",
    targetRepoWrite: String = "never",
    sidecarWrite: String = "never",
    jsonSupported: Bool = true,
    audience: [String] = ["human", "agent"],
    routeRole: String? = nil,
    flags: [String] = ["--json"],
    examples: [String] = []
) -> CommandEntry {
    CommandEntry(
        name: name,
        path: path ?? name.split(separator: " ").map(String.init),
        summary: "Test command",
        audience: audience,
        mutation: mutation,
        targetRepoWrite: targetRepoWrite,
        sidecarWrite: sidecarWrite,
        jsonSupported: jsonSupported,
        routeRole: routeRole,
        canonicalCommand: name,
        aliasOf: nil,
        outputSchema: "test_payload",
        examples: examples,
        flags: flags.map { CommandFlag(option: $0, dest: nil, help: nil, required: false, choices: nil) },
        docs: []
    )
}

do {
    try runLearningChecks()

    let start = makeCommand(name: "start", flags: ["--repo", "--json", "--no-update"])
    try check(start.appCoverage == .native, "start should use the native overview coverage")
    try check(
        start.safeArguments(selectedRepo: "/tmp/example repo") == ["start", "--repo", "/tmp/example repo", "--no-update", "--json"],
        "start preview should force --no-update and --json"
    )

    let update = makeCommand(
        name: "update",
        mutation: "writes-target-by-default",
        targetRepoWrite: "writes-target-by-default",
        flags: ["--repo", "--json", "--all", "--dry-run", "--apply"]
    )
    try check(
        update.safeArguments(selectedRepo: "/tmp/example") == ["update", "--repo", "/tmp/example", "--dry-run", "--json"],
        "update should use selected repo dry-run arguments"
    )

    let closeoutFix = makeCommand(
        name: "closeout-fix",
        mutation: "launches-write-agent",
        targetRepoWrite: "via launched agent in --apply mode",
        sidecarWrite: "with --apply",
        flags: ["--repo", "--json", "--apply", "--jsonl", "--agent", "--timeout-seconds"]
    )
    try check(closeoutFix.appCoverage == .native, "closeout-fix should have a native one-click app surface")
    try check(
        closeoutFix.safeArguments(selectedRepo: "/tmp/example") == ["closeout-fix", "--repo", "/tmp/example", "--json"],
        "command-browser closeout-fix should preview only"
    )

    let targetImport = makeCommand(
        name: "target import",
        path: ["target", "import"],
        mutation: "writes-local-kit-registry-with-apply",
        sidecarWrite: "with --apply",
        flags: ["--root", "--json", "--dry-run", "--apply"]
    )
    try check(targetImport.appCoverage == .previewInApp, "target import should be preview-only")
    try check(targetImport.safeArguments(selectedRepo: nil) == nil, "target import should need a selected root")
    try check(
        targetImport.safeArguments(selectedRepo: "/tmp/root") == ["target", "import", "--root", "/tmp/root", "--dry-run", "--json"],
        "target import should force --dry-run"
    )

    let doctor = makeCommand(name: "doctor", flags: ["--repo", "--json", "--write-sidecar"])
    try check(doctor.appCoverage == .runInApp, "doctor should run in app without optional write-sidecar")
    try check(
        doctor.safeArguments(selectedRepo: "/tmp/repo") == ["doctor", "--repo", "/tmp/repo", "--json"],
        "doctor should omit optional sidecar write flag"
    )

    let status = makeCommand(
        name: "status",
        flags: ["--repo", "--json"],
        examples: ["kit status --repo /path/to/repo --json"]
    )

    let agentOnly = makeCommand(
        name: "agent-note",
        audience: ["agent"],
        routeRole: "agent-only",
        flags: ["--repo", "--json"]
    )
    try check(CommandBrowserScope.recommended.includes(status), "status should be recommended")
    try check(CommandBrowserScope.readOnly.includes(doctor), "doctor should appear in read-only commands")
    try check(CommandBrowserScope.preview.includes(update), "update should appear in preview commands")
    try check(!CommandBrowserScope.recommended.includes(agentOnly), "agent-only commands should stay out of recommended")
    try check(CommandBrowserScope.agentTools.includes(agentOnly), "agent-only commands should appear in the agent scope")

    let commandMap = CommandMapPayload(cli: nil, commands: [agentOnly, update, doctor, status])
    try check(
        commandMap.visibleCommands(in: .recommended).map(\.displayName).contains("status"),
        "recommended command map should include status"
    )
    try check(
        !commandMap.visibleCommands(in: .recommended).map(\.displayName).contains("agent-note"),
        "recommended command map should not include agent-only commands"
    )

    try expectThrows("unsafe update should be blocked") {
        try KitProcessRunner.validateReadOnlyCommand(["update", "--repo", "/tmp/repo"])
    }
    try KitProcessRunner.validateReadOnlyCommand(["update", "--repo", "/tmp/repo", "--dry-run", "--json"])
    try expectThrows("automation handoff without dry-run should be blocked") {
        try KitProcessRunner.validateReadOnlyCommand(["automation-handoff", "--repo", "/tmp/repo", "--json"])
    }
    try KitProcessRunner.validateReadOnlyCommand(["automation-handoff", "--repo", "/tmp/repo", "--dry-run", "--json"])
    try expectThrows("generic closeout-fix apply should be blocked") {
        try KitProcessRunner.validateReadOnlyCommand(["closeout-fix", "--repo", "/tmp/repo", "--apply", "--jsonl"])
    }
    try KitProcessRunner.validateReadOnlyCommand(["closeout-fix", "--repo", "/tmp/repo", "--json"])
    try KitProcessRunner.validateCloseoutFixCommand(["closeout-fix", "--repo", "/tmp/repo", "--apply", "--jsonl"])
    try KitProcessRunner.validateCloseoutFixCommand(["closeout-fix", "--repo", "/tmp/repo", "--apply", "--jsonl", "--agent", "codex"])
    try KitProcessRunner.validateAllowedWriteCommand(["target", "import", "--root", "/tmp/root", "--apply", "--json"])
    try KitProcessRunner.validateAllowedWriteCommand(["target", "prune-missing", "--apply", "--json"])
    try KitProcessRunner.validateAllowedWriteCommand(["target", "update-all", "--apply", "--json"])
    try KitProcessRunner.validateAllowedWriteCommand(["worktree", "prune", "--root", "/tmp/root", "--apply", "--json"])
    try expectThrows("setup should not be app write allowlisted") {
        try KitProcessRunner.validateAllowedWriteCommand(["setup", "--preset", "agentic", "--json"])
    }
    try expectThrows("global update should not be app write allowlisted") {
        try KitProcessRunner.validateAllowedWriteCommand(["update", "--global", "--json"])
    }
    try expectThrows("write-sidecar should not be app write allowlisted") {
        try KitProcessRunner.validateAllowedWriteCommand(["verify", "--write-sidecar", "--json"])
    }
    try expectThrows("closeout-fix dedicated runner should reject custom agent commands") {
        try KitProcessRunner.validateCloseoutFixCommand([
            "closeout-fix",
            "--repo",
            "/tmp/repo",
            "--apply",
            "--jsonl",
            "--agent-command",
            "danger"
        ])
    }
    let finalLine = """
    {"event":"final-payload","payload":{"command":"closeout-fix","result":"applied","human_summary":{"title":"Guided closeout applied","plain_reason":"Strict closeout passed after the guided workflow.","recommended_action":"Review the receipt."},"blocker_explanations":[],"commits":[{"short_sha":"abc123","subject":"Add lane"}],"receipts":[{"path":"/tmp/receipt.json","kind":"closeout-fix"}],"branches_pushed":[],"worktrees_pruned":[],"blockers":[],"exit_code":0}}
    """
    let finalPayload = try JSONDecoder().decode(CloseoutFixFinalPayloadLine.self, from: Data(finalLine.utf8))
    try check(finalPayload.payload?.result == "applied", "closeout-fix final JSONL payload should decode")
    try check(finalPayload.payload?.commits?.first?.subject == "Add lane", "closeout-fix commits should decode")
    try check(finalPayload.payload?.humanSummary?.title == "Guided closeout applied", "closeout-fix human summary should decode")

    try check(
        status.terminalCommand(selectedRepo: "/tmp/example repo") == "kit status --repo '/tmp/example repo' --json",
        "terminal commands should shell-quote repo paths"
    )
    try check(LoginItemService.label(for: .enabled) == "Enabled", "login item enabled label should be clear")
    try check(LoginItemService.label(for: .requiresApproval) == "Needs Approval", "login item approval label should be explicit")
    try check(
        LoginItemService.message(for: .requiresApproval).contains("System Settings"),
        "login item approval message should point to System Settings"
    )
    try check(
        LoginItemService.message(for: .notRegistered).contains("not registered"),
        "login item off message should describe unregistered state"
    )

    let tempDir = FileManager.default.temporaryDirectory.appendingPathComponent("KitCompanionChecks-\(UUID().uuidString)", isDirectory: true)
    try FileManager.default.createDirectory(at: tempDir, withIntermediateDirectories: true)
    let noisyCommand = tempDir.appendingPathComponent("noisy-kit")
    try """
    #!/usr/bin/env python3
    print("x" * 200000)
    """.write(to: noisyCommand, atomically: true, encoding: .utf8)
    try FileManager.default.setAttributes([.posixPermissions: 0o755], ofItemAtPath: noisyCommand.path)

    let semaphore = DispatchSemaphore(value: 0)
    var noisyResult: Result<KitCommandResult, Error>?
    Task {
        do {
            noisyResult = .success(try await KitProcessRunner().run(arguments: [], kitPath: noisyCommand.path))
        } catch {
            noisyResult = .failure(error)
        }
        semaphore.signal()
    }
    if semaphore.wait(timeout: .now() + 5) == .timedOut {
        throw CheckFailure.failed("runner should drain command output larger than the default pipe buffer")
    }
    switch noisyResult {
    case .success(let result):
        try check(result.succeeded, "large-output command should succeed")
        try check(result.stdout.count > 100000, "large-output command stdout should be captured")
    case .failure(let error):
        throw CheckFailure.failed("large-output command failed: \(error)")
    case .none:
        throw CheckFailure.failed("large-output command did not report a result")
    }

    let streamingCommand = tempDir.appendingPathComponent("streaming-kit")
    try """
    #!/usr/bin/env python3
    import json
    import time

    print(json.dumps({"event":"job-started","job_id":"job","text":"live start"}), flush=True)
    time.sleep(0.7)
    print(json.dumps({"event":"final-payload","payload":{"command":"closeout-fix","mode":"apply","result":"applied","commits":[],"branches_pushed":[],"worktrees_pruned":[],"receipts":[],"blockers":[],"exit_code":0}}), flush=True)
    """.write(to: streamingCommand, atomically: true, encoding: .utf8)
    try FileManager.default.setAttributes([.posixPermissions: 0o755], ofItemAtPath: streamingCommand.path)

    let streamEventSemaphore = DispatchSemaphore(value: 0)
    let streamDoneSemaphore = DispatchSemaphore(value: 0)
    let streamTimestamps = StreamingTimestampRecorder()
    var streamResult: Result<CloseoutFixPayload, Error>?
    Task {
        do {
            streamResult = .success(
                try await KitProcessRunner().runCloseoutFix(
                    arguments: ["closeout-fix", "--repo", tempDir.path, "--apply", "--jsonl"],
                    kitPath: streamingCommand.path
                ) { event in
                    if event.event == "job-started" {
                        streamTimestamps.recordEventIfNeeded(signal: streamEventSemaphore)
                    }
                }
            )
        } catch {
            streamResult = .failure(error)
        }
        streamTimestamps.recordDone()
        streamDoneSemaphore.signal()
    }
    if streamEventSemaphore.wait(timeout: .now() + 1) == .timedOut {
        throw CheckFailure.failed("closeout-fix runner should stream JSONL events before command exit")
    }
    if streamDoneSemaphore.wait(timeout: .now() + 5) == .timedOut {
        throw CheckFailure.failed("closeout-fix streaming command should finish")
    }
    switch streamResult {
    case .success(let payload):
        try check(payload.result == "applied", "closeout-fix streaming final payload should decode")
    case .failure(let error):
        throw CheckFailure.failed("closeout-fix streaming command failed: \(error)")
    case .none:
        throw CheckFailure.failed("closeout-fix streaming command did not report a result")
    }
    let timestamps = streamTimestamps.snapshot()
    let eventAt = timestamps.eventAt
    let doneAt = timestamps.doneAt
    if let eventAt, let doneAt {
        try check(doneAt.timeIntervalSince(eventAt) > 0.25, "closeout-fix event should arrive before final payload")
    } else {
        throw CheckFailure.failed("closeout-fix streaming timestamps were not recorded")
    }

    let blockedStreamingCommand = tempDir.appendingPathComponent("blocked-streaming-kit")
    try """
    #!/usr/bin/env python3
    import json

    print(json.dumps({"event":"job-finished","result":"blocked","exit_code":2}), flush=True)
    print(json.dumps({"event":"final-payload","payload":{"command":"closeout-fix","mode":"apply","result":"blocked","human_summary":{"title":"Guided closeout blocked after partial progress","plain_reason":"The source tree is clean, but evidence cleanup is still needed.","recommended_action":"Review task evidence."},"blocker_explanations":[{"code":"missing_final_receipts","title":"Missing task receipts","plain_reason":"Some old tasks are missing receipts.","recommended_action":"Link durable receipts.","count":3}],"commits":[],"branches_pushed":[],"worktrees_pruned":[],"receipts":[],"blockers":["Final strict closeout-plan did not pass."],"exit_code":2}}), flush=True)
    raise SystemExit(2)
    """.write(to: blockedStreamingCommand, atomically: true, encoding: .utf8)
    try FileManager.default.setAttributes([.posixPermissions: 0o755], ofItemAtPath: blockedStreamingCommand.path)

    let blockedSemaphore = DispatchSemaphore(value: 0)
    var blockedResult: Result<CloseoutFixPayload, Error>?
    Task {
        do {
            blockedResult = .success(
                try await KitProcessRunner().runCloseoutFix(
                    arguments: ["closeout-fix", "--repo", tempDir.path, "--apply", "--jsonl"],
                    kitPath: blockedStreamingCommand.path
                ) { _ in }
            )
        } catch {
            blockedResult = .failure(error)
        }
        blockedSemaphore.signal()
    }
    if blockedSemaphore.wait(timeout: .now() + 5) == .timedOut {
        throw CheckFailure.failed("blocked closeout-fix streaming command should finish")
    }
    switch blockedResult {
    case .success(let payload):
        try check(payload.result == "blocked", "blocked closeout-fix final payload should return without throwing")
        try check(payload.humanSummary?.title == "Guided closeout blocked after partial progress", "blocked closeout-fix should decode human summary")
        try check(payload.blockerExplanations?.first?.title == "Missing task receipts", "blocked closeout-fix should decode blocker explanation")
    case .failure(let error):
        throw CheckFailure.failed("blocked closeout-fix streaming command should not throw when final payload is present: \(error)")
    case .none:
        throw CheckFailure.failed("blocked closeout-fix streaming command did not report a result")
    }
    try? FileManager.default.removeItem(at: tempDir)

    print("KitCompanionChecks passed")
} catch {
    fputs("KitCompanionChecks failed: \(error)\n", stderr)
    exit(1)
}
