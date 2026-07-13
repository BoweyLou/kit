import AppKit
import Foundation
import UniformTypeIdentifiers

@MainActor
final class LearningStore: ObservableObject {
    struct EventRecordForm: Equatable {
        var kind: LearningEventKind = .observation
        var summary = ""
        var evidenceText = ""
        var outcome: LearningEventOutcome = .confirmed
        var source: LearningEventSource = .human
        var privacyLabel: LearningPrivacyLabel = .internal
        var approvalConfirmed = false

        var evidenceItems: [String] {
            evidenceText
                .split(whereSeparator: \.isNewline)
                .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
                .filter { !$0.isEmpty }
        }
    }

    struct ProposalCreateForm: Equatable {
        var title = ""
        var classification: LearningProposalClassification = .documentation
        var scopesText = ""
        var recommendedChange = ""
        var evidenceEventIDsText = ""
        var privacyLabel: LearningPrivacyLabel = .internal

        var scopes: [String] {
            scopesText
                .split(whereSeparator: { $0 == "," || $0.isNewline })
                .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
                .filter { !$0.isEmpty }
        }

        var evidenceEventIDs: [String] {
            evidenceEventIDsText
                .split(whereSeparator: { $0 == "," || $0.isNewline })
                .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
                .filter { !$0.isEmpty }
        }
    }

    struct DecisionRecordForm: Equatable {
        var proposalID = ""
        var outcome: LearningDecisionOutcome = .approved
        var decider = ""
        var rationale = ""
        var followUpText = ""
        var humanReviewConfirmed = false

        var followUpItems: [String] {
            followUpText
                .split(whereSeparator: \.isNewline)
                .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
                .filter { !$0.isEmpty }
        }
    }

    struct ContextBuildForm: Equatable {
        var decisionID = ""
    }

    struct ThreadSummaryImportForm: Equatable {
        var fileURL: URL?
        var summaryID: String?
        var reportedAt: String?
        var interactionCount: Int?
        var redactedSummary: String?
        var validationMessage: String?
    }

    struct UpstreamExportForm: Equatable {
        var decisionID = ""
        var privacyLabel: LearningPrivacyLabel = .publicOK
        var redactionConfirmed = false
    }

    struct LifecycleIndicator: Equatable {
        let title: String
        let systemImage: String
        let detail: String
    }

    struct FactualCount: Identifiable, Equatable {
        let id: String
        let label: String
        let value: String
        let systemImage: String
    }

    enum PendingActionKind: Equatable {
        case eventRecord(EventRecordForm)
        case proposalCreate(ProposalCreateForm)
        case decisionRecord(DecisionRecordForm)
        case contextBuild(ContextBuildForm)
        case threadSummaryImport(ThreadSummaryImportForm, LearningThreadSummaryInput)
        case upstreamExport(UpstreamExportForm)
    }

    struct PendingAction: Identifiable, Equatable {
        let id = UUID()
        let title: String
        let confirmationText: String
        let commandPreview: String
        let repo: String
        let selectionGeneration: Int
        let kind: PendingActionKind
    }

    @Published private(set) var repo: String?
    @Published private(set) var status: LearningStatusPayload?
    @Published private(set) var eventList: LearningEventListPayload?
    @Published private(set) var proposalList: LearningProposalListPayload?
    @Published private(set) var decisionList: LearningDecisionListPayload?
    @Published private(set) var contextList: LearningContextListPayload?
    @Published private(set) var threadSummaryList: LearningThreadSummaryListPayload?
    @Published private(set) var upstreamList: LearningUpstreamListPayload?
    @Published private(set) var upstreamReconcile: LearningUpstreamReconcilePayload?
    @Published private(set) var evaluation: LearningEvaluatePayload?
    @Published private(set) var isLoading = false
    @Published private(set) var isExecutingWrite = false
    @Published var pendingAction: PendingAction?
    @Published var errorMessage: String?
    @Published var successMessage: String?
    @Published var eventRecordForm = EventRecordForm()
    @Published var proposalCreateForm = ProposalCreateForm()
    @Published var decisionRecordForm = DecisionRecordForm()
    @Published var contextBuildForm = ContextBuildForm()
    @Published var threadSummaryImportForm = ThreadSummaryImportForm()
    @Published var upstreamExportForm = UpstreamExportForm()

    private let runner: LearningRunning
    private let kitPathProvider: @Sendable () -> String
    private let fileManager: FileManager
    private var selectionGeneration = 0
    private var loadGeneration = 0
    private var loadTask: Task<Void, Never>?
    private var writeTask: Task<Void, Never>?

    init(
        runner: LearningRunning = LearningRunner(),
        kitPathProvider: @escaping @Sendable () -> String = { KitSettings.kitBinaryPath() },
        fileManager: FileManager = .default
    ) {
        self.runner = runner
        self.kitPathProvider = kitPathProvider
        self.fileManager = fileManager
    }

    var warnings: [String] {
        var combined: [String] = []
        combined += eventList?.warnings ?? []
        combined += proposalList?.warnings ?? []
        combined += decisionList?.warnings ?? []
        combined += contextList?.warnings ?? []
        combined += threadSummaryList?.warnings ?? []
        combined += upstreamList?.warnings ?? []
        combined += upstreamReconcile?.warnings ?? []
        combined += evaluation?.warnings ?? []
        return Array(NSOrderedSet(array: combined)) as? [String] ?? combined
    }

    var pendingProposals: [LearningProposal] {
        (proposalList?.proposals ?? []).filter { $0.status.localizedCaseInsensitiveContains("pending") }
    }

    var approvedDecisions: [LearningDecision] {
        (decisionList?.decisions ?? []).filter { $0.outcome == .approved }
    }

    var factualCounts: [FactualCount] {
        [
            FactualCount(id: "events", label: "Events", value: "\(eventList?.count ?? 0)", systemImage: "text.badge.plus"),
            FactualCount(id: "proposals", label: "Proposals", value: "\(proposalList?.count ?? 0)", systemImage: "lightbulb"),
            FactualCount(id: "decisions", label: "Decisions", value: "\(decisionList?.count ?? 0)", systemImage: "checkmark.seal"),
            FactualCount(id: "contexts", label: "Contexts", value: "\(contextList?.count ?? 0)", systemImage: "books.vertical"),
            FactualCount(id: "thread-summaries", label: "Thread Summaries", value: "\(threadSummaryList?.count ?? 0)", systemImage: "text.quote"),
            FactualCount(id: "upstream", label: "Source-Review", value: "\(upstreamList?.count ?? 0)", systemImage: "square.and.arrow.up"),
            FactualCount(id: "reconcile", label: "Reconcile", value: "\(upstreamReconcile?.count ?? 0)", systemImage: "arrow.triangle.branch"),
            FactualCount(id: "facts", label: "Schema-valid", value: "\(evaluation?.facts.schemaValidEvents ?? 0)", systemImage: "checkmark.shield"),
            FactualCount(id: "thread-facts", label: "Eval Thread Events", value: "\(evaluation?.facts.threadSummaryEvents ?? 0)", systemImage: "text.redaction")
        ]
    }

    var lifecycleIndicator: LifecycleIndicator {
        if repo == nil {
            return LifecycleIndicator(title: "No repo selected", systemImage: "folder.badge.questionmark", detail: "Choose a target repo to load learning state.")
        }
        if isExecutingWrite {
            return LifecycleIndicator(title: "Write in progress", systemImage: "square.and.pencil", detail: "A confirmed sidecar write is running with typed contract validation.")
        }
        if isLoading {
            return LifecycleIndicator(title: "Loading", systemImage: "arrow.clockwise", detail: "Reading learning status, histories, evaluation, and reconciliation data.")
        }
        if let successMessage {
            return LifecycleIndicator(title: "Ready", systemImage: "checkmark.circle", detail: successMessage)
        }
        if let errorMessage {
            return LifecycleIndicator(title: "Attention needed", systemImage: "exclamationmark.triangle", detail: errorMessage)
        }
        return LifecycleIndicator(title: "Ready", systemImage: "checkmark.circle", detail: "Learning read models are loaded for the selected repo.")
    }

    var writesAllowed: Bool {
        status?.policy.enabled == true && status?.policyState == "active" && status?.policy.ownership == "target"
    }

    var terminalOnlyGuidance: String {
        "Learning policy writes are unavailable here. Use Terminal with a valid enabled learning policy for this repo."
    }

    var evaluationCaveat: LearningEvaluationCaveat? {
        evaluation?.caveat
    }

    func selectRepo(_ newRepo: String?) {
        selectionGeneration += 1
        loadGeneration += 1
        loadTask?.cancel()
        writeTask?.cancel()

        repo = newRepo
        clearFeatureState()

        guard let newRepo else {
            return
        }
        startLoad(for: newRepo, selectionGeneration: selectionGeneration, loadGeneration: loadGeneration)
    }

    func ensureLoaded() {
        guard repo != nil,
              status == nil || eventList == nil || proposalList == nil || decisionList == nil || contextList == nil ||
                threadSummaryList == nil || upstreamList == nil || upstreamReconcile == nil || evaluation == nil else {
            return
        }
        refresh()
    }

    func refresh() {
        guard let repo else {
            return
        }
        loadGeneration += 1
        loadTask?.cancel()
        errorMessage = nil
        successMessage = nil
        startLoad(for: repo, selectionGeneration: selectionGeneration, loadGeneration: loadGeneration)
    }

    func cancelPendingAction() {
        pendingAction = nil
    }

    func chooseThreadSummaryFile() {
        let panel = NSOpenPanel()
        panel.canChooseFiles = true
        panel.canChooseDirectories = false
        panel.allowsMultipleSelection = false
        panel.allowedContentTypes = [.json]
        panel.prompt = "Select JSON"
        guard panel.runModal() == .OK, let url = panel.url else {
            return
        }

        do {
            let input = try LearningThreadSummaryInput.loadStrict(from: url)
            threadSummaryImportForm.fileURL = url
            threadSummaryImportForm.summaryID = input.summaryID
            threadSummaryImportForm.reportedAt = input.reportedAt
            threadSummaryImportForm.interactionCount = input.aggregate.interactionCount
            threadSummaryImportForm.redactedSummary = input.aggregate.redactedSummary
            threadSummaryImportForm.validationMessage = "Validated strict JSON input."
            errorMessage = nil
        } catch {
            threadSummaryImportForm.fileURL = nil
            threadSummaryImportForm.summaryID = nil
            threadSummaryImportForm.reportedAt = nil
            threadSummaryImportForm.interactionCount = nil
            threadSummaryImportForm.redactedSummary = nil
            threadSummaryImportForm.validationMessage = nil
            errorMessage = error.localizedDescription
        }
    }

    func prepareEventRecord() {
        guard guardWriteAvailability() else { return }
        guard let repo else { return }
        do {
            var eventSnapshot = eventRecordForm
            eventSnapshot.approvalConfirmed = true
            let command = try LearningCommandBuilder.eventRecord(
                repo: repo,
                kind: eventSnapshot.kind,
                summary: eventSnapshot.summary,
                evidence: eventSnapshot.evidenceItems,
                outcome: eventSnapshot.outcome,
                source: eventSnapshot.source,
                privacyLabel: eventSnapshot.privacyLabel,
                approved: eventSnapshot.approvalConfirmed
            )
            pendingAction = PendingAction(
                title: "Confirm event record",
                confirmationText: "Record a supervised learning event for the selected repo sidecar.",
                commandPreview: KitCommandLine.render(arguments: command.arguments),
                repo: repo,
                selectionGeneration: selectionGeneration,
                kind: .eventRecord(eventSnapshot)
            )
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func prepareProposalCreate() {
        guard guardWriteAvailability() else { return }
        guard let repo else { return }
        do {
            let command = try LearningCommandBuilder.proposalCreate(
                repo: repo,
                title: proposalCreateForm.title,
                classification: proposalCreateForm.classification,
                scopes: proposalCreateForm.scopes,
                recommendedChange: proposalCreateForm.recommendedChange,
                evidenceEventIDs: proposalCreateForm.evidenceEventIDs,
                privacyLabel: proposalCreateForm.privacyLabel
            )
            pendingAction = PendingAction(
                title: "Confirm proposal create",
                confirmationText: "Create a non-executing proposal in the repo sidecar for later human review.",
                commandPreview: KitCommandLine.render(arguments: command.arguments),
                repo: repo,
                selectionGeneration: selectionGeneration,
                kind: .proposalCreate(proposalCreateForm)
            )
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func prepareDecisionRecord() {
        guard guardWriteAvailability() else { return }
        guard let repo else { return }
        do {
            let command = try LearningCommandBuilder.decisionRecord(
                repo: repo,
                proposalID: decisionRecordForm.proposalID,
                outcome: decisionRecordForm.outcome,
                decider: decisionRecordForm.decider,
                rationale: decisionRecordForm.rationale,
                followUp: decisionRecordForm.followUpItems,
                humanReviewConfirmed: decisionRecordForm.humanReviewConfirmed
            )
            pendingAction = PendingAction(
                title: "Confirm decision record",
                confirmationText: "Record a reviewed decision against an existing learning proposal.",
                commandPreview: KitCommandLine.render(arguments: command.arguments),
                repo: repo,
                selectionGeneration: selectionGeneration,
                kind: .decisionRecord(decisionRecordForm)
            )
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func prepareContextBuild() {
        guard guardWriteAvailability() else { return }
        guard let repo else { return }
        do {
            let command = try LearningCommandBuilder.contextBuild(repo: repo, decisionID: contextBuildForm.decisionID)
            pendingAction = PendingAction(
                title: "Confirm context build",
                confirmationText: "Build sidecar-only guidance context for a reviewed decision.",
                commandPreview: KitCommandLine.render(arguments: command.arguments),
                repo: repo,
                selectionGeneration: selectionGeneration,
                kind: .contextBuild(contextBuildForm)
            )
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func prepareThreadSummaryImport() {
        guard guardWriteAvailability() else { return }
        guard let repo, let url = threadSummaryImportForm.fileURL else { return }
        do {
            let input = try LearningThreadSummaryInput.loadStrict(from: url)
            var updated = threadSummaryImportForm
            updated.summaryID = input.summaryID
            updated.reportedAt = input.reportedAt
            updated.interactionCount = input.aggregate.interactionCount
            updated.redactedSummary = input.aggregate.redactedSummary
            updated.validationMessage = "Validated strict JSON input."
            threadSummaryImportForm = updated

            let command = try LearningCommandBuilder.threadSummaryImport(repo: repo, inputPath: url.path, approved: true)
            pendingAction = PendingAction(
                title: "Confirm thread summary import",
                confirmationText: "The selected JSON is validated now. On confirmation, the app creates a private temporary copy, imports from that copy, then deletes it.",
                commandPreview: KitCommandLine.render(arguments: command.arguments),
                repo: repo,
                selectionGeneration: selectionGeneration,
                kind: .threadSummaryImport(updated, input)
            )
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func prepareUpstreamExport() {
        guard guardWriteAvailability() else { return }
        guard let repo else { return }
        do {
            let command = try LearningCommandBuilder.upstreamExport(
                repo: repo,
                decisionID: upstreamExportForm.decisionID,
                privacyLabel: upstreamExportForm.privacyLabel,
                redactionConfirmed: upstreamExportForm.redactionConfirmed
            )
            pendingAction = PendingAction(
                title: "Confirm source-review candidate export",
                confirmationText: "Create a source-review candidate with explicit redaction confirmation. Only public-ok and internal exports are allowed.",
                commandPreview: KitCommandLine.render(arguments: command.arguments),
                repo: repo,
                selectionGeneration: selectionGeneration,
                kind: .upstreamExport(upstreamExportForm)
            )
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func confirmPendingAction() {
        guard let pendingAction else {
            return
        }
        guard pendingAction.selectionGeneration == selectionGeneration, pendingAction.repo == repo else {
            self.pendingAction = nil
            return
        }
        self.pendingAction = nil
        errorMessage = nil
        successMessage = nil
        isExecutingWrite = true
        writeTask?.cancel()

        writeTask = Task {
            do {
                try await execute(pendingAction)
                guard isSelectionCurrent(repo: pendingAction.repo, selectionGeneration: pendingAction.selectionGeneration) else {
                    return
                }
                successMessage = "\(pendingAction.title) completed."
                refresh()
            } catch is CancellationError {
            } catch {
                guard isSelectionCurrent(repo: pendingAction.repo, selectionGeneration: pendingAction.selectionGeneration) else {
                    return
                }
                errorMessage = error.localizedDescription
            }
            if isSelectionCurrent(repo: pendingAction.repo, selectionGeneration: pendingAction.selectionGeneration) {
                isExecutingWrite = false
            }
        }
    }

    private func execute(_ action: PendingAction) async throws {
        switch action.kind {
        case .eventRecord(let form):
            let command = try LearningCommandBuilder.eventRecord(
                repo: action.repo,
                kind: form.kind,
                summary: form.summary,
                evidence: form.evidenceItems,
                outcome: form.outcome,
                source: form.source,
                privacyLabel: form.privacyLabel,
                approved: form.approvalConfirmed
            )
            _ = try await runner.run(
                LearningEventRecordPayload.self,
                command: command,
                selectedRepo: action.repo,
                kitPath: kitPathProvider()
            )
        case .proposalCreate(let form):
            let command = try LearningCommandBuilder.proposalCreate(
                repo: action.repo,
                title: form.title,
                classification: form.classification,
                scopes: form.scopes,
                recommendedChange: form.recommendedChange,
                evidenceEventIDs: form.evidenceEventIDs,
                privacyLabel: form.privacyLabel
            )
            _ = try await runner.run(
                LearningProposalCreatePayload.self,
                command: command,
                selectedRepo: action.repo,
                kitPath: kitPathProvider()
            )
        case .decisionRecord(let form):
            let command = try LearningCommandBuilder.decisionRecord(
                repo: action.repo,
                proposalID: form.proposalID,
                outcome: form.outcome,
                decider: form.decider,
                rationale: form.rationale,
                followUp: form.followUpItems,
                humanReviewConfirmed: form.humanReviewConfirmed
            )
            _ = try await runner.run(
                LearningDecisionRecordPayload.self,
                command: command,
                selectedRepo: action.repo,
                kitPath: kitPathProvider()
            )
        case .contextBuild(let form):
            let command = try LearningCommandBuilder.contextBuild(repo: action.repo, decisionID: form.decisionID)
            _ = try await runner.run(
                LearningContextBuildPayload.self,
                command: command,
                selectedRepo: action.repo,
                kitPath: kitPathProvider()
            )
        case .threadSummaryImport(_, let input):
            let temporaryURL = try input.writeTemporary(fileManager: fileManager)
            defer { try? fileManager.removeItem(at: temporaryURL) }
            guard isSelectionCurrent(repo: action.repo, selectionGeneration: action.selectionGeneration) else {
                return
            }
            let command = try LearningCommandBuilder.threadSummaryImport(repo: action.repo, inputPath: temporaryURL.path, approved: true)
            _ = try await runner.run(
                LearningThreadSummaryImportPayload.self,
                command: command,
                selectedRepo: action.repo,
                kitPath: kitPathProvider()
            )
        case .upstreamExport(let form):
            let command = try LearningCommandBuilder.upstreamExport(
                repo: action.repo,
                decisionID: form.decisionID,
                privacyLabel: form.privacyLabel,
                redactionConfirmed: form.redactionConfirmed
            )
            _ = try await runner.run(
                LearningUpstreamExportPayload.self,
                command: command,
                selectedRepo: action.repo,
                kitPath: kitPathProvider()
            )
        }
    }

    private func startLoad(for repo: String, selectionGeneration: Int, loadGeneration: Int) {
        isLoading = true
        loadTask = Task {
            do {
                async let status = runRead(LearningStatusPayload.self, command: try LearningCommandBuilder.status(repo: repo), repo: repo)
                async let events = runRead(LearningEventListPayload.self, command: try LearningCommandBuilder.eventList(repo: repo, limit: 50), repo: repo)
                async let proposals = runRead(LearningProposalListPayload.self, command: try LearningCommandBuilder.proposalList(repo: repo, limit: 50), repo: repo)
                async let decisions = runRead(LearningDecisionListPayload.self, command: try LearningCommandBuilder.decisionList(repo: repo, limit: 50), repo: repo)
                async let contexts = runRead(LearningContextListPayload.self, command: try LearningCommandBuilder.contextList(repo: repo, limit: 50), repo: repo)
                async let threadSummaries = runRead(LearningThreadSummaryListPayload.self, command: try LearningCommandBuilder.threadSummaryList(repo: repo, limit: 50), repo: repo)
                async let upstream = runRead(LearningUpstreamListPayload.self, command: try LearningCommandBuilder.upstreamList(repo: repo, limit: 50), repo: repo)
                async let reconcile = runRead(LearningUpstreamReconcilePayload.self, command: try LearningCommandBuilder.upstreamReconcile(repo: repo, limit: 50), repo: repo)
                async let evaluate = runRead(LearningEvaluatePayload.self, command: try LearningCommandBuilder.evaluate(repo: repo), repo: repo)

                let snapshot = try await (
                    status,
                    events,
                    proposals,
                    decisions,
                    contexts,
                    threadSummaries,
                    upstream,
                    reconcile,
                    evaluate
                )

                guard isCurrentLoad(repo: repo, selectionGeneration: selectionGeneration, loadGeneration: loadGeneration) else {
                    return
                }
                self.status = snapshot.0
                self.eventList = snapshot.1
                self.proposalList = snapshot.2
                self.decisionList = snapshot.3
                self.contextList = snapshot.4
                self.threadSummaryList = snapshot.5
                self.upstreamList = snapshot.6
                self.upstreamReconcile = snapshot.7
                self.evaluation = snapshot.8
                self.errorMessage = nil
            } catch is CancellationError {
            } catch {
                guard isCurrentLoad(repo: repo, selectionGeneration: selectionGeneration, loadGeneration: loadGeneration) else {
                    return
                }
                self.errorMessage = error.localizedDescription
            }

            if isCurrentLoad(repo: repo, selectionGeneration: selectionGeneration, loadGeneration: loadGeneration) {
                isLoading = false
            }
        }
    }

    private func runRead<T: Decodable & LearningPayloadMetadata>(_ type: T.Type, command: LearningCommand, repo: String) async throws -> T {
        try await runner.run(type, command: command, selectedRepo: repo, kitPath: kitPathProvider())
    }

    private func clearFeatureState() {
        status = nil
        eventList = nil
        proposalList = nil
        decisionList = nil
        contextList = nil
        threadSummaryList = nil
        upstreamList = nil
        upstreamReconcile = nil
        evaluation = nil
        pendingAction = nil
        errorMessage = nil
        successMessage = nil
        isLoading = false
        isExecutingWrite = false
        eventRecordForm = EventRecordForm()
        proposalCreateForm = ProposalCreateForm()
        decisionRecordForm = DecisionRecordForm()
        contextBuildForm = ContextBuildForm()
        threadSummaryImportForm = ThreadSummaryImportForm()
        upstreamExportForm = UpstreamExportForm()
    }

    private func guardWriteAvailability() -> Bool {
        errorMessage = nil
        successMessage = nil
        guard writesAllowed else {
            errorMessage = terminalOnlyGuidance
            return false
        }
        return true
    }

    private func isSelectionCurrent(repo: String, selectionGeneration: Int) -> Bool {
        self.repo == repo && self.selectionGeneration == selectionGeneration
    }

    private func isCurrentLoad(repo: String, selectionGeneration: Int, loadGeneration: Int) -> Bool {
        self.repo == repo && self.selectionGeneration == selectionGeneration && self.loadGeneration == loadGeneration
    }
}
