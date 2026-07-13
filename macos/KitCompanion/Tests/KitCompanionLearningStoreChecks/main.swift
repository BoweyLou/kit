import Foundation

enum CheckFailure: Error, CustomStringConvertible {
    case failed(String)
    var description: String { if case .failed(let message) = self { return message }; return "check failed" }
}

func check(_ condition: @autoclosure () -> Bool, _ message: String) throws {
    guard condition() else { throw CheckFailure.failed(message) }
}

private let repoA = "/tmp/kit-learning-store-a"
private let repoB = "/tmp/kit-learning-store-b"
private let eventID = "evt-0123456789abcdef0123"

private final class FakeLearningRunner: LearningRunning, @unchecked Sendable {
    private let lock = NSLock()
    private var recordedCommands: [LearningCommand] = []
    private var temporaryInputPath: String?

    var commands: [LearningCommand] {
        lock.lock(); defer { lock.unlock() }
        return recordedCommands
    }

    var capturedTemporaryInputPath: String? {
        lock.lock(); defer { lock.unlock() }
        return temporaryInputPath
    }

    func run<T: Decodable & LearningPayloadMetadata>(
        _ type: T.Type,
        command: LearningCommand,
        selectedRepo: String,
        kitPath: String
    ) async throws -> T {
        record(command)

        if selectedRepo == repoA {
            try await Task.sleep(nanoseconds: 150_000_000)
        }

        let data = try JSONSerialization.data(withJSONObject: fixture(route: command.route, repo: selectedRepo), options: [])
        let payload = try JSONDecoder().decode(T.self, from: data)
        try LearningPayloadValidator.validate(payload, expectedCommand: command.route, selectedRepo: selectedRepo)
        return payload
    }

    private func record(_ command: LearningCommand) {
        lock.lock()
        recordedCommands.append(command)
        if command.route == .threadSummaryImport,
           let input = command.arguments.first(where: { $0.hasPrefix("--input=") }) {
            temporaryInputPath = String(input.dropFirst("--input=".count))
        }
        lock.unlock()
    }

    private func fixture(route: LearningCommandRoute, repo: String) -> [String: Any] {
        let identity = LearningPayloadValidator.sidecarRepoIdentity(selectedRepo: repo)
        let sidecarRoot = LearningPayloadValidator.expectedSidecarStateDirectory(selectedRepo: repo)
        let metadata: [String: Any] = [
            "schema_version": 1,
            "command": route.rawValue,
            "repo": repo,
            "target_repo_writes": ["performed": false, "paths": [], "reason": "no writes"],
            "sidecar_writes": route.writesSidecar
                ? ["performed": true, "paths": ["\(sidecarRoot)/events/\(eventID).json"], "reason": "approved sidecar write"]
                : ["performed": false, "paths": [], "reason": "no writes"],
            "global_writes": ["performed": false, "paths": [], "reason": "no writes"],
            "sidecar_state": [
                "repo_state_dir": sidecarRoot,
                "repo": ["root": identity.root, "hash": identity.hash, "id": identity.id]
            ],
            "exit_code": 0
        ]

        switch route {
        case .status:
            return metadata.merging([
                "policy_state": "active",
                "policy": ["state": "active", "path": "\(repo)/.agent-workflows/learning-policy.json", "ownership": "target", "enabled": true, "policy_id": "supervised-learning", "schema_version": 1],
                "learning_paths": ["policy": "\(repo)/.agent-workflows/learning-policy.json", "schemas": [:], "sidecar": ["root": sidecarRoot]],
                "safe_next_commands": [],
                "write_guarantees": ["target_repo_writes": false, "sidecar_writes": false, "global_tool_writes": false, "note": "read-only supervised learning"]
            ]) { _, new in new }
        case .eventList:
            return listMetadata(metadata, action: "event-list", extra: ["events_path": "\(sidecarRoot)/events.json", "events": [], "count": 0, "warnings": []])
        case .proposalList:
            return listMetadata(metadata, action: "proposal-list", extra: ["proposals": [], "count": 0, "warnings": []])
        case .decisionList:
            return listMetadata(metadata, action: "decision-list", extra: ["decisions": [], "count": 0, "warnings": []])
        case .contextList:
            return listMetadata(metadata, action: "context-list", extra: ["contexts": [], "count": 0, "warnings": [], "sidecar_only_guidance": true])
        case .threadSummaryList:
            return listMetadata(metadata, action: "thread-summary-list", extra: ["events_path": "\(sidecarRoot)/thread-summaries.json", "events": [], "count": 0, "warnings": []])
        case .upstreamList, .upstreamReconcile:
            return listMetadata(metadata, action: route == .upstreamList ? "upstream-list" : "upstream-reconcile", extra: ["candidates": [], "count": 0, "warnings": [], "rollout_guidance": reviewGuidance()])
        case .evaluate:
            return listMetadata(metadata, action: "evaluate", extra: ["facts": ["thread_summary_events": 0, "schema_valid_events": 0, "upstream_candidates": 0], "caveat": ["not_effectiveness_claim": true, "note": "descriptive only"], "warnings": [], "rollout_guidance": reviewGuidance()])
        case .eventRecord:
            return writeMetadata(metadata, repo: repo, action: "event-record", extra: ["event": event(repo: repo, capture: "explicit-cli-input"), "event_path": "\(sidecarRoot)/events/\(eventID).json"])
        case .threadSummaryImport:
            return writeMetadata(metadata, repo: repo, action: "thread-summary-import", extra: ["event": event(repo: repo, capture: "thread-summary-import"), "event_path": "\(sidecarRoot)/events/\(eventID).json", "input_contract": ["schema": "thread-summary-v1", "raw_transcript_scan": false, "history_mining": false, "network_calls": false, "note": "redacted aggregate only"]])
        default:
            fatalError("unexpected write route in store harness: \(route)")
        }
    }

    private func listMetadata(_ metadata: [String: Any], action: String, extra: [String: Any]) -> [String: Any] {
        metadata.merging(extra.merging(["action": action]) { _, new in new }) { _, new in new }
    }

    private func writeMetadata(_ metadata: [String: Any], repo: String, action: String, extra: [String: Any]) -> [String: Any] {
        let policy: [String: Any] = ["state": "active", "path": "\(repo)/.agent-workflows/learning-policy.json", "ownership": "target", "enabled": true, "policy_id": "supervised-learning", "schema_version": 1]
        return metadata.merging(extra.merging(["action": action, "policy_state": "active", "policy": policy, "gate": ["state": "approved", "reason": "explicit human approval"]]) { _, new in new }) { _, new in new }
    }

    private func event(repo: String, capture: String) -> [String: Any] {
        ["schema_version": 1, "event_id": eventID, "occurred_at": "2026-07-13T00:00:00Z", "policy_id": "supervised-learning", "repo": repo, "kind": "observation", "summary": "Harness event", "evidence": ["bounded store harness"], "outcome": "confirmed", "provenance": ["source": "human", "capture": capture], "privacy_label": "internal", "supervision": ["human_approval_required": true, "approval_state": "approved", "approval_flag": true]]
    }

    private func reviewGuidance() -> [String: Any] {
        ["source_review_required": true, "automatic_propagation": false, "normal_source_workflow": ["review", "accept"], "note": "review only"]
    }
}

enum KitSettings {
    static func kitBinaryPath() -> String { "/tmp/kit-test" }
}

@main
struct KitCompanionLearningStoreChecks {
    static func main() async {
        do {
            try await runChecks()
            print("KitCompanionLearningStoreChecks passed")
        } catch {
            fputs("KitCompanionLearningStoreChecks failed: \(error)\n", stderr)
            exit(1)
        }
    }

    @MainActor
    private static func runChecks() async throws {
        let runner = FakeLearningRunner()
        let store = LearningStore(runner: runner, kitPathProvider: { KitSettings.kitBinaryPath() })

        store.selectRepo(repoA)
        store.selectRepo(repoB)
        try await waitUntil { !store.isLoading }
        try check(store.repo == repoB && store.status?.repo == repoB, "latest repository selection must win")

        let initialB = runner.commands.filter { $0.arguments.contains("--repo=\(repoB)") }
        let expectedReadRoutes = Set([LearningCommandRoute.status, .eventList, .proposalList, .decisionList, .contextList, .threadSummaryList, .upstreamList, .upstreamReconcile, .evaluate].map(\.rawValue))
        try check(initialB.count == 9 && Set(initialB.map { $0.route.rawValue }) == expectedReadRoutes, "initial B load must be exactly the nine read routes")
        try check(initialB.allSatisfy { !$0.writesSidecar }, "initial B load must not write")

        store.eventRecordForm.summary = "A valid supervised event"
        store.eventRecordForm.evidenceText = "Harness evidence"
        try check(!store.eventRecordForm.approvalConfirmed, "event approval must default to false")
        store.prepareEventRecord()
        try check(store.pendingAction != nil, "valid event form should prepare")
        if case .eventRecord(let snapshot)? = store.pendingAction?.kind {
            try check(snapshot.approvalConfirmed, "prepared event snapshot must carry approval")
        } else {
            throw CheckFailure.failed("prepared action must be an event record")
        }
        try check(store.pendingAction?.commandPreview.contains("--approved") == true, "event preview must include --approved")
        try check(store.pendingAction?.commandPreview.contains("--approval-state=approved") == true, "event preview must include approved state")
        store.cancelPendingAction()
        try check(runner.commands.filter { $0.route.writesSidecar }.isEmpty, "cancel must not call a write route")

        store.prepareEventRecord()
        store.confirmPendingAction()
        try await waitUntil { !store.isExecutingWrite }
        let eventWrites = runner.commands.filter { $0.route == .eventRecord }
        try check(eventWrites.count == 1, "confirming event must call eventRecord once")
        try check(runner.commands.filter { $0.arguments.contains("--repo=\(repoB)") }.count > initialB.count, "event confirmation must refresh reads")

        let inputURL = FileManager.default.temporaryDirectory.appendingPathComponent("strict-thread-summary-\(UUID().uuidString).json")
        defer { try? FileManager.default.removeItem(at: inputURL) }
        let source = """
        {"schema_version":1,"summary_id":"tsum-0123456789abcdef0123","reported_at":"2026-07-13T00:00:00Z","redaction":{"human_confirmed":true,"raw_transcript_excluded":true,"raw_feedback_excluded":true,"raw_event_content_excluded":true,"private_content_excluded":true},"aggregate":{"interaction_count":1,"outcome_counts":{"confirmed":1,"inconclusive":0,"regressed":0},"classification_counts":{"documentation":1},"redacted_summary":"One bounded test interaction."}}
        """
        try Data(source.utf8).write(to: inputURL)
        store.threadSummaryImportForm.fileURL = inputURL
        store.prepareThreadSummaryImport()
        try check(store.pendingAction != nil, "strict thread summary should prepare")
        store.confirmPendingAction()
        try await waitUntil { !store.isExecutingWrite && runner.capturedTemporaryInputPath != nil }
        let captured = try require(runner.capturedTemporaryInputPath)
        try check(!FileManager.default.fileExists(atPath: captured), "app-owned temporary import path must be deleted after completion")
    }

    @MainActor
    private static func waitUntil(_ predicate: @escaping () -> Bool) async throws {
        let deadline = Date().addingTimeInterval(3)
        while !predicate() && Date() < deadline { try await Task.sleep(nanoseconds: 10_000_000) }
        try check(predicate(), "bounded wait timed out")
    }

    private static func require<T>(_ value: T?) throws -> T {
        guard let value else { throw CheckFailure.failed("expected captured temporary input path") }
        return value
    }
}
