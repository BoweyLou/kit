import SwiftUI

private enum LearningDashboardSection: String, CaseIterable, Identifiable {
    case status = "Status"
    case event = "Event"
    case proposal = "Proposal"
    case decision = "Decision"
    case context = "Context"
    case threadImport = "Thread Import"
    case sourceReview = "Source Review"
    case artifacts = "Artifacts"

    var id: String { rawValue }

    var systemImage: String {
        switch self {
        case .status: "checkmark.shield"
        case .event: "plus.bubble"
        case .proposal: "lightbulb"
        case .decision: "checkmark.seal"
        case .context: "books.vertical"
        case .threadImport: "text.quote"
        case .sourceReview: "square.and.arrow.up"
        case .artifacts: "archivebox"
        }
    }
}

private enum LearningArtifactKind: String, CaseIterable, Identifiable {
    case events = "Event history"
    case proposals = "Proposal history"
    case decisions = "Decision history"
    case contexts = "Context history"
    case threadSummaries = "Thread summary history"
    case sourceReviewCandidates = "Source-review candidates"
    case reconciliation = "Reconciliation history"

    var id: String { rawValue }
}

struct LearningDashboardView: View {
    @ObservedObject var store: LearningStore
    @State private var selectedSection: LearningDashboardSection = .status
    @State private var selectedArtifactKind: LearningArtifactKind = .events

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Picker("Learning section", selection: $selectedSection) {
                    ForEach(LearningDashboardSection.allCases) { section in
                        Label(section.rawValue, systemImage: section.systemImage)
                            .tag(section)
                    }
                }
                .pickerStyle(.menu)
                .accessibilityIdentifier("learning-section-picker")
                .accessibilityLabel("Learning section")

                selectedPanel
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .sheet(item: pendingActionBinding) { action in
            LearningConfirmationSheet(store: store, action: action)
        }
        .onAppear {
            store.ensureLoaded()
        }
    }

    @ViewBuilder
    private var selectedPanel: some View {
        switch selectedSection {
        case .status:
            statusSection
                .accessibilityIdentifier("learning-panel-status")
        case .event:
            eventRecordForm
                .accessibilityIdentifier("learning-panel-event")
        case .proposal:
            proposalCreateForm
                .accessibilityIdentifier("learning-panel-proposal")
        case .decision:
            decisionSection
                .accessibilityIdentifier("learning-panel-decision")
        case .context:
            contextBuildForm
                .accessibilityIdentifier("learning-panel-context")
        case .threadImport:
            threadSummaryForm
                .accessibilityIdentifier("learning-panel-thread-import")
        case .sourceReview:
            upstreamExportForm
                .accessibilityIdentifier("learning-panel-source-review")
        case .artifacts:
            artifactsSection
                .accessibilityIdentifier("learning-panel-artifacts")
        }
    }

    private var statusSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            header
            countsGrid
            statusOperations
        }
    }

    private var decisionSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            if !store.pendingProposals.isEmpty || !store.approvedDecisions.isEmpty {
                queuePanel
            }
            decisionRecordForm
        }
    }

    private var pendingActionBinding: Binding<LearningStore.PendingAction?> {
        Binding(
            get: { store.pendingAction },
            set: { action in
                if action == nil {
                    store.cancelPendingAction()
                }
            }
        )
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .top, spacing: 16) {
                statusCard(
                    title: "Policy",
                    systemImage: store.writesAllowed ? "checkmark.shield" : "shield.slash",
                    detail: store.status?.policyState ?? "unknown",
                    footnote: store.status?.policy.path ?? "No policy path reported."
                )
                statusCard(
                    title: "Privacy",
                    systemImage: "hand.raised",
                    detail: store.status?.writeGuarantees.note ?? "No privacy guarantees reported.",
                    footnote: store.status?.policy.ownership ?? "Ownership unavailable."
                )
                statusCard(
                    title: "Lifecycle",
                    systemImage: store.lifecycleIndicator.systemImage,
                    detail: store.lifecycleIndicator.title,
                    footnote: store.lifecycleIndicator.detail
                )
            }

            if let caveat = store.evaluationCaveat {
                Label(caveat.note, systemImage: caveat.notEffectivenessClaim ? "info.circle" : "checkmark.circle")
                    .font(.callout)
                    .foregroundStyle(.secondary)
                    .accessibilityIdentifier("learning-evaluation-caveat")
            }

            if !store.warnings.isEmpty {
                VStack(alignment: .leading, spacing: 6) {
                    Text("Warnings")
                        .font(.headline)
                    ForEach(store.warnings, id: \.self) { warning in
                        Label(warning, systemImage: "exclamationmark.triangle")
                            .foregroundStyle(.orange)
                    }
                }
            }
        }
    }

    private var countsGrid: some View {
        LazyVGrid(columns: [GridItem(.adaptive(minimum: 145), spacing: 10)], alignment: .leading, spacing: 10) {
            ForEach(store.factualCounts) { count in
                VStack(alignment: .leading, spacing: 4) {
                    Label(count.label, systemImage: count.systemImage)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Text(count.value)
                        .font(.title3.weight(.semibold))
                }
                .padding(10)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color(nsColor: .controlBackgroundColor), in: RoundedRectangle(cornerRadius: 8))
                .overlay {
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(Color(nsColor: .separatorColor), lineWidth: 0.5)
                }
            }
        }
    }

    private var queuePanel: some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 12) {
                if !store.pendingProposals.isEmpty {
                    Text("Pending review queue")
                        .font(.headline)
                    ForEach(store.pendingProposals.prefix(6)) { proposal in
                        VStack(alignment: .leading, spacing: 2) {
                            Text(proposal.title)
                                .font(.callout.weight(.semibold))
                            Text("\(proposal.proposalID) • \(proposal.classification.rawValue) • \(proposal.privacyLabel.rawValue)")
                                .font(.caption.monospaced())
                                .foregroundStyle(.secondary)
                            Text(proposal.recommendedChange)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                }

                if !store.approvedDecisions.isEmpty {
                    Divider()
                    Text("Approved decisions")
                        .font(.headline)
                    ForEach(store.approvedDecisions.prefix(6)) { decision in
                        VStack(alignment: .leading, spacing: 2) {
                            Text(decision.decisionID)
                                .font(.callout.weight(.semibold))
                            Text("\(decision.proposalID) • \(decision.decider)")
                                .font(.caption.monospaced())
                                .foregroundStyle(.secondary)
                            Text(decision.rationale)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        } label: {
            Label("Review Queue", systemImage: "list.bullet.clipboard")
        }
    }

    private var statusOperations: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack(alignment: .center, spacing: 12) {
                Label("Refresh and guidance", systemImage: "arrow.clockwise")
                    .font(.title3.weight(.semibold))
                Spacer()
                Button {
                    store.refresh()
                } label: {
                    Label("Refresh", systemImage: "arrow.clockwise")
                }
                .keyboardShortcut("r", modifiers: [.command, .shift])
                .disabled(store.repo == nil || store.isLoading || store.isExecutingWrite)
                .accessibilityIdentifier("learning-refresh")
            }

            if !store.writesAllowed {
                Label(store.terminalOnlyGuidance, systemImage: "terminal")
                    .foregroundStyle(.secondary)
                    .accessibilityIdentifier("learning-terminal-guidance")
            }
        }
    }

    private var eventRecordForm: some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 10) {
                Picker("Kind", selection: $store.eventRecordForm.kind) {
                    ForEach(LearningEventKind.allCases) { kind in
                        Text(kind.rawValue).tag(kind)
                    }
                }
                Picker("Outcome", selection: $store.eventRecordForm.outcome) {
                    ForEach(LearningEventOutcome.allCases) { outcome in
                        Text(outcome.rawValue).tag(outcome)
                    }
                }
                Picker("Source", selection: $store.eventRecordForm.source) {
                    ForEach(LearningEventSource.allCases) { source in
                        Text(source.rawValue).tag(source)
                    }
                }
                Picker("Privacy", selection: $store.eventRecordForm.privacyLabel) {
                    ForEach(LearningPrivacyLabel.allCases) { privacy in
                        Text(privacy.rawValue).tag(privacy)
                    }
                }
                TextField("Summary", text: $store.eventRecordForm.summary, axis: .vertical)
                    .lineLimit(2...4)
                    .accessibilityIdentifier("learning-event-summary")
                TextField("Evidence, one item per line", text: $store.eventRecordForm.evidenceText, axis: .vertical)
                    .lineLimit(3...5)
                    .accessibilityIdentifier("learning-event-evidence")
                Text("Confirmation records this exact event with --approved.")
                    .font(.callout)
                    .foregroundStyle(.secondary)
                Button("Prepare event record") {
                    store.prepareEventRecord()
                }
                .keyboardShortcut("e", modifiers: [.command, .shift])
                .help("Prepare event record (Command-Shift-E)")
                .disabled(!store.writesAllowed || store.isExecutingWrite || store.eventRecordForm.summary.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                .accessibilityIdentifier("learning-event-prepare")
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        } label: {
            Label("Event Record", systemImage: "plus.bubble")
        }
    }

    private var proposalCreateForm: some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 10) {
                TextField("Title", text: $store.proposalCreateForm.title)
                    .accessibilityIdentifier("learning-proposal-title")
                Picker("Classification", selection: $store.proposalCreateForm.classification) {
                    ForEach(LearningProposalClassification.allCases) { classification in
                        Text(classification.rawValue).tag(classification)
                    }
                }
                Picker("Privacy", selection: $store.proposalCreateForm.privacyLabel) {
                    ForEach(LearningPrivacyLabel.allCases) { privacy in
                        Text(privacy.rawValue).tag(privacy)
                    }
                }
                TextField("Scopes, comma or newline separated", text: $store.proposalCreateForm.scopesText, axis: .vertical)
                    .lineLimit(2...4)
                TextField("Recommended change", text: $store.proposalCreateForm.recommendedChange, axis: .vertical)
                    .lineLimit(2...4)
                TextField("Evidence event IDs, comma or newline separated", text: $store.proposalCreateForm.evidenceEventIDsText, axis: .vertical)
                    .lineLimit(2...4)
                Button("Prepare proposal create") {
                    store.prepareProposalCreate()
                }
                .keyboardShortcut("p", modifiers: [.command, .shift])
                .help("Prepare proposal create (Command-Shift-P)")
                .disabled(!store.writesAllowed || store.isExecutingWrite)
                .accessibilityIdentifier("learning-proposal-prepare")
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        } label: {
            Label("Proposal Create", systemImage: "lightbulb")
        }
    }

    private var decisionRecordForm: some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 10) {
                TextField("Proposal ID", text: $store.decisionRecordForm.proposalID)
                    .accessibilityIdentifier("learning-decision-proposal-id")
                Picker("Outcome", selection: $store.decisionRecordForm.outcome) {
                    ForEach(LearningDecisionOutcome.allCases) { outcome in
                        Text(outcome.rawValue).tag(outcome)
                    }
                }
                TextField("Decider", text: $store.decisionRecordForm.decider)
                TextField("Rationale", text: $store.decisionRecordForm.rationale, axis: .vertical)
                    .lineLimit(2...4)
                TextField("Follow-up, one item per line", text: $store.decisionRecordForm.followUpText, axis: .vertical)
                    .lineLimit(2...4)
                Toggle("Human review confirmed", isOn: $store.decisionRecordForm.humanReviewConfirmed)
                Button("Prepare decision record") {
                    store.prepareDecisionRecord()
                }
                .keyboardShortcut("d", modifiers: [.command, .shift])
                .help("Prepare decision record (Command-Shift-D)")
                .disabled(!store.writesAllowed || store.isExecutingWrite)
                .accessibilityIdentifier("learning-decision-prepare")
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        } label: {
            Label("Decision Record", systemImage: "checkmark.seal")
        }
    }

    private var contextBuildForm: some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 10) {
                TextField("Decision ID", text: $store.contextBuildForm.decisionID)
                    .accessibilityIdentifier("learning-context-decision-id")
                Button("Prepare context build") {
                    store.prepareContextBuild()
                }
                .keyboardShortcut("c", modifiers: [.command, .shift])
                .help("Prepare context build (Command-Shift-C)")
                .disabled(!store.writesAllowed || store.isExecutingWrite)
                .accessibilityIdentifier("learning-context-prepare")
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        } label: {
            Label("Context Build", systemImage: "books.vertical")
        }
    }

    private var threadSummaryForm: some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Button("Choose JSON File") {
                        store.chooseThreadSummaryFile()
                    }
                    .help("Choose a JSON file")
                    .accessibilityIdentifier("learning-thread-summary-choose")
                    Spacer()
                    if let url = store.threadSummaryImportForm.fileURL {
                        Text(KitDisplay.shortPath(url.path))
                            .font(.caption.monospaced())
                            .foregroundStyle(.secondary)
                            .lineLimit(1)
                            .truncationMode(.middle)
                    }
                }
                if let summaryID = store.threadSummaryImportForm.summaryID {
                    Text("Summary ID: \(summaryID)")
                        .font(.callout.weight(.semibold))
                }
                if let reportedAt = store.threadSummaryImportForm.reportedAt {
                    Text("Reported at: \(reportedAt)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                if let interactionCount = store.threadSummaryImportForm.interactionCount {
                    Text("Interactions: \(interactionCount)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                if let redactedSummary = store.threadSummaryImportForm.redactedSummary {
                    Text(redactedSummary)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .fixedSize(horizontal: false, vertical: true)
                }
                if let validationMessage = store.threadSummaryImportForm.validationMessage {
                    Label(validationMessage, systemImage: "checkmark.shield")
                        .foregroundStyle(.secondary)
                }
                Button("Prepare thread-summary import") {
                    store.prepareThreadSummaryImport()
                }
                .keyboardShortcut("i", modifiers: [.command, .shift])
                .help("Prepare thread-summary import (Command-Shift-I)")
                .disabled(!store.writesAllowed || store.isExecutingWrite || store.threadSummaryImportForm.fileURL == nil)
                .accessibilityIdentifier("learning-thread-summary-prepare")
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        } label: {
            Label("Thread Summary Import", systemImage: "text.quote")
        }
    }

    private var upstreamExportForm: some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 10) {
                TextField("Decision ID", text: $store.upstreamExportForm.decisionID)
                    .accessibilityIdentifier("learning-upstream-decision-id")
                Picker("Privacy", selection: $store.upstreamExportForm.privacyLabel) {
                    Text(LearningPrivacyLabel.publicOK.rawValue).tag(LearningPrivacyLabel.publicOK)
                    Text(LearningPrivacyLabel.internal.rawValue).tag(LearningPrivacyLabel.internal)
                }
                Toggle("Redaction confirmed", isOn: $store.upstreamExportForm.redactionConfirmed)
                Button("Create source-review candidate") {
                    store.prepareUpstreamExport()
                }
                .keyboardShortcut("u", modifiers: [.command, .shift])
                .help("Create source-review candidate (Command-Shift-U)")
                .disabled(!store.writesAllowed || store.isExecutingWrite)
                .accessibilityIdentifier("learning-upstream-prepare")
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        } label: {
            Label("Upstream Export", systemImage: "square.and.arrow.up")
        }
    }

    private var artifactsSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Picker("Artifact kind", selection: $selectedArtifactKind) {
                ForEach(LearningArtifactKind.allCases) { artifact in
                    Text(artifact.rawValue).tag(artifact)
                }
            }
            .pickerStyle(.menu)
            .accessibilityIdentifier("learning-artifact-kind-picker")
            .accessibilityLabel("Artifact kind")

            selectedArtifactHistory
        }
    }

    @ViewBuilder
    private var selectedArtifactHistory: some View {
        switch selectedArtifactKind {
        case .events:
            historyPanel(
                title: "Event history",
                systemImage: "clock.arrow.circlepath",
                emptyText: "No events loaded.",
                accessibilityIdentifier: "learning-history-events",
                items: store.eventList?.events ?? []
            ) { event in
                VStack(alignment: .leading, spacing: 2) {
                    Text(event.summary)
                        .font(.callout.weight(.semibold))
                    Text("\(event.eventID) • \(event.occurredAt) • \(event.kind.rawValue) • \(event.privacyLabel.rawValue)")
                        .font(.caption.monospaced())
                        .foregroundStyle(.secondary)
                }
            }
        case .proposals:
            historyPanel(
                title: "Proposal history",
                systemImage: "lightbulb",
                emptyText: "No proposals loaded.",
                accessibilityIdentifier: "learning-history-proposals",
                items: store.proposalList?.proposals ?? []
            ) { proposal in
                VStack(alignment: .leading, spacing: 2) {
                    Text(proposal.title)
                        .font(.callout.weight(.semibold))
                    Text("\(proposal.proposalID) • \(proposal.status) • \(proposal.classification.rawValue)")
                        .font(.caption.monospaced())
                        .foregroundStyle(.secondary)
                    Text(proposal.recommendedChange)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
        case .decisions:
            historyPanel(
                title: "Decision history",
                systemImage: "checkmark.seal",
                emptyText: "No decisions loaded.",
                accessibilityIdentifier: "learning-history-decisions",
                items: store.decisionList?.decisions ?? []
            ) { decision in
                VStack(alignment: .leading, spacing: 2) {
                    Text(decision.decisionID)
                        .font(.callout.weight(.semibold))
                    Text("\(decision.proposalID) • \(decision.outcome.rawValue) • \(decision.decidedAt)")
                        .font(.caption.monospaced())
                        .foregroundStyle(.secondary)
                    Text(decision.rationale)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
        case .contexts:
            historyPanel(
                title: "Context history",
                systemImage: "books.vertical",
                emptyText: "No contexts loaded.",
                accessibilityIdentifier: "learning-history-contexts",
                items: store.contextList?.contexts ?? []
            ) { context in
                VStack(alignment: .leading, spacing: 2) {
                    Text(context.contextID)
                        .font(.callout.weight(.semibold))
                    Text("\(context.lineage.decisionID) • \(context.lineage.proposalID) • \(context.retention.expiresAt)")
                        .font(.caption.monospaced())
                        .foregroundStyle(.secondary)
                    Text(context.guidance.recommendedChange)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
        case .threadSummaries:
            historyPanel(
                title: "Thread summary history",
                systemImage: "text.quote",
                emptyText: "No thread summary imports loaded.",
                accessibilityIdentifier: "learning-history-thread-summaries",
                items: store.threadSummaryList?.events ?? []
            ) { event in
                VStack(alignment: .leading, spacing: 2) {
                    Text(event.summary)
                        .font(.callout.weight(.semibold))
                    Text("\(event.eventID) • \(event.occurredAt) • \(event.outcome.rawValue)")
                        .font(.caption.monospaced())
                        .foregroundStyle(.secondary)
                }
            }
        case .sourceReviewCandidates:
            historyPanel(
                title: "Source-review candidates",
                systemImage: "square.and.arrow.up",
                emptyText: "No source-review candidates loaded.",
                accessibilityIdentifier: "learning-history-source-review",
                items: store.upstreamList?.candidates ?? []
            ) { candidate in
                VStack(alignment: .leading, spacing: 2) {
                    Text(candidate.candidateID)
                        .font(.callout.weight(.semibold))
                    Text("\(candidate.lineage.decisionID) • \(candidate.privacyLabel.rawValue) • \(candidate.createdAt)")
                        .font(.caption.monospaced())
                        .foregroundStyle(.secondary)
                    Text(candidate.recommendation.recommendedChange)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
        case .reconciliation:
            historyPanel(
                title: "Reconciliation history",
                systemImage: "arrow.triangle.branch",
                emptyText: "No reconciliation candidates loaded.",
                accessibilityIdentifier: "learning-history-reconciliation",
                items: store.upstreamReconcile?.candidates ?? []
            ) { candidate in
                VStack(alignment: .leading, spacing: 2) {
                    Text(candidate.candidateID)
                        .font(.callout.weight(.semibold))
                    Text("\(candidate.status) • revalidation \(candidate.revalidationRequired ? "required" : "not required")")
                        .font(.caption.monospaced())
                        .foregroundStyle(.secondary)
                    Text("Baseline: \(candidate.baseline.sourceRef) @ \(candidate.baseline.version)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
        }
    }

    private func statusCard(title: String, systemImage: String, detail: String, footnote: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Label(title, systemImage: systemImage)
                .font(.headline)
            Text(detail)
                .font(.callout.weight(.semibold))
                .fixedSize(horizontal: false, vertical: true)
            Text(footnote)
                .font(.caption)
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(nsColor: .controlBackgroundColor), in: RoundedRectangle(cornerRadius: 8))
        .overlay {
            RoundedRectangle(cornerRadius: 8)
                .stroke(Color(nsColor: .separatorColor), lineWidth: 0.5)
        }
    }

    private func historyPanel<Item: Identifiable, Content: View>(
        title: String,
        systemImage: String,
        emptyText: String,
        accessibilityIdentifier: String,
        items: [Item],
        @ViewBuilder content: @escaping (Item) -> Content
    ) -> some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 8) {
                if items.isEmpty {
                    Text(emptyText)
                        .foregroundStyle(.secondary)
                } else {
                    ForEach(items.prefix(8)) { item in
                        content(item)
                    }
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        } label: {
            Label(title, systemImage: systemImage)
        }
        .accessibilityIdentifier(accessibilityIdentifier)
    }
}

private struct LearningConfirmationSheet: View {
    @ObservedObject var store: LearningStore
    let action: LearningStore.PendingAction
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(action.title)
                .font(.title3.weight(.semibold))
            Text(action.confirmationText)
                .foregroundStyle(.secondary)
            Text("Exact command preview")
                .font(.headline)
            ScrollView {
                Text(action.commandPreview)
                    .font(.system(.body, design: .monospaced))
                    .textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(10)
                    .background(Color(nsColor: .textBackgroundColor), in: RoundedRectangle(cornerRadius: 8))
            }
            .frame(minHeight: 110, maxHeight: 180)
            HStack {
                Spacer()
                Button("Cancel") {
                    store.cancelPendingAction()
                    dismiss()
                }
                .keyboardShortcut(.cancelAction)
                Button("Confirm") {
                    store.confirmPendingAction()
                    dismiss()
                }
                .keyboardShortcut(.defaultAction)
            }
        }
        .padding(20)
        .frame(minWidth: 540)
        .accessibilityIdentifier("learning-confirmation-sheet")
    }
}
