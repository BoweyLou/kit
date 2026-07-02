import SwiftUI

struct DashboardView: View {
    @ObservedObject var store: KitCompanionStore

    var body: some View {
        NavigationSplitView {
            List(selection: targetSelection) {
                ForEach(store.targets) { target in
                    TargetRow(target: target)
                        .tag(target.id)
                }
            }
            .listStyle(.sidebar)
            .navigationTitle("Targets")
            .toolbar {
                Button {
                    store.refreshTargets()
                } label: {
                    Image(systemName: "arrow.clockwise")
                }
                .help("Refresh targets")
            }
        } detail: {
            DetailPane(store: store)
        }
        .task {
            if store.targets.isEmpty {
                store.refreshTargets()
            } else if store.detail == nil {
                store.loadSelectedDetail()
            }
            if store.commandMap == nil {
                store.loadCommandMap()
            }
        }
    }

    private var targetSelection: Binding<String?> {
        Binding(
            get: { store.selectedTargetID },
            set: { store.selectTargetID($0) }
        )
    }
}

private struct TargetRow: View {
    let target: KitTarget

    var body: some View {
        HStack(spacing: 10) {
            Image(systemName: target.isDirty ? "exclamationmark.circle.fill" : "checkmark.circle")
                .foregroundStyle(target.isDirty ? .orange : .green)
            VStack(alignment: .leading, spacing: 2) {
                Text(target.name)
                    .lineLimit(1)
                Text(target.displayStatus)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .padding(.vertical, 3)
    }
}

private struct DetailPane: View {
    @ObservedObject var store: KitCompanionStore

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            header

            if let error = store.errorMessage {
                Label(error, systemImage: "exclamationmark.triangle")
                    .foregroundStyle(.red)
            } else if let message = store.message {
                Text(message)
                    .foregroundStyle(.secondary)
            }

            switch store.dashboardSection {
            case .overview:
                if let detail = store.detail {
                    RepoOverviewView(store: store, detail: detail)
                } else {
                    ContentUnavailableView("Select a target", systemImage: "folder.badge.gearshape")
                }
            case .commands:
                CommandBrowserView(store: store)
            case .workflows:
                WorkflowPanelsView(store: store, mode: .workflows)
            case .batch:
                WorkflowPanelsView(store: store, mode: .batch)
            }

            Spacer(minLength: 0)
        }
        .padding(22)
        .confirmationDialog(
            "Run guided closeout?",
            isPresented: $store.isConfirmingCloseoutFix,
            titleVisibility: .visible
        ) {
            Button("Run closeout-fix --apply", role: .destructive) {
                store.runCloseoutFix()
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("Kit will run closeout-fix with --apply for the selected target and stream commits, pushes, receipts, and blockers back into this window.")
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .firstTextBaseline, spacing: 12) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(store.selectedTarget?.name ?? "kit")
                        .font(.title2.weight(.semibold))
                    Text(store.selectedTarget.map { KitDisplay.shortPath($0.root) } ?? "Optional macOS companion")
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                        .truncationMode(.middle)
                }

                Spacer()

                Picker("Section", selection: $store.dashboardSection) {
                    ForEach(DashboardSection.allCases) { section in
                        Text(section.label).tag(section)
                    }
                }
                .pickerStyle(.segmented)
                .labelsHidden()
                .frame(width: 360)
            }

            HStack(spacing: 8) {
                Button {
                    store.openSelectedInFinder()
                } label: {
                    Label("Open Folder", systemImage: "folder")
                }
                .disabled(store.selectedTarget == nil)

                Button {
                    store.openSelectedInTerminal()
                } label: {
                    Label("Open Terminal", systemImage: "terminal")
                }
                .disabled(store.selectedTarget == nil)

                Button {
                    store.previewSelectedTargetUpdate()
                } label: {
                    Label("Preview Target Update", systemImage: "doc.text.magnifyingglass")
                }
                .disabled(store.selectedTarget == nil)

                Spacer()

                Button {
                    store.checkForUpdates()
                } label: {
                    Label("Check App Update", systemImage: "arrow.down.app")
                }
            }
        }
    }
}

private struct RepoOverviewView: View {
    @ObservedObject var store: KitCompanionStore
    let detail: RepoDetail

    private var hasCloseoutActivity: Bool {
        store.isRunningCloseoutFix || store.closeoutFixPayload != nil || !store.closeoutFixEvents.isEmpty
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                statusStrip
                RecommendedActionPanel(store: store, detail: detail)

                if let blockers = detail.closeout?.claimBlockers, !blockers.isEmpty {
                    BlockersPanel(blockers: blockers)
                }

                NextCommandsPanel(store: store, steps: detail.start?.nextSteps ?? [])

                if hasCloseoutActivity {
                    DisclosureGroup("Closeout Fix Activity") {
                        CloseoutFixJobView(
                            payload: store.closeoutFixPayload,
                            events: store.closeoutFixEvents,
                            isRunning: store.isRunningCloseoutFix
                        )
                        .padding(.top, 8)
                    }
                }

                if let preview = store.updatePreview {
                    DisclosureGroup("Update Preview") {
                        UpdatePreviewView(preview: preview)
                            .padding(.top, 8)
                    }
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private var statusStrip: some View {
        let worktree = detail.status?.gitWorktreeState
        let dirtyCount = worktree?.count ?? detail.target.dirtyCount
        let isDirty = worktree?.dirty == true || detail.target.isDirty
        let closeoutState = detail.closeout?.completionState ?? "unknown"
        let canClaimDone = detail.closeout?.canClaimDone == true
        let drift = detail.status?.kitDrift?.classification ?? "unknown"
        let driftWarns = detail.status?.kitDrift?.hasWarning == true

        return LazyVGrid(columns: [GridItem(.adaptive(minimum: 155), spacing: 10)], alignment: .leading, spacing: 10) {
            StatusTile(
                title: "Worktree",
                value: isDirty ? "\(dirtyCount) changed" : "Clean",
                systemImage: isDirty ? "exclamationmark.circle.fill" : "checkmark.circle.fill",
                tone: isDirty ? .warning : .success
            )
            StatusTile(
                title: "Closeout",
                value: canClaimDone ? "Claimable" : closeoutState.capitalized,
                systemImage: canClaimDone ? "checkmark.seal.fill" : "flag.fill",
                tone: canClaimDone ? .success : .warning
            )
            StatusTile(
                title: "Kit",
                value: drift.capitalized,
                systemImage: driftWarns ? "arrow.triangle.2.circlepath.circle.fill" : "checkmark.circle.fill",
                tone: driftWarns ? .warning : .success
            )
            StatusTile(
                title: "Mode",
                value: detail.start?.mode?.selected ?? "unknown",
                systemImage: "dial.low.fill",
                tone: .neutral
            )
        }
    }
}

private struct StatusTile: View {
    let title: String
    let value: String
    let systemImage: String
    let tone: StatusTone

    var body: some View {
        HStack(spacing: 9) {
            Image(systemName: systemImage)
                .foregroundStyle(tone.color)
                .frame(width: 18)
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text(value)
                    .font(.callout.weight(.semibold))
                    .lineLimit(1)
            }
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

private enum StatusTone {
    case success
    case warning
    case neutral

    var color: Color {
        switch self {
        case .success:
            return .green
        case .warning:
            return .orange
        case .neutral:
            return .accentColor
        }
    }
}

private struct RecommendedActionPanel: View {
    @ObservedObject var store: KitCompanionStore
    let detail: RepoDetail

    private var dirtyCount: Int {
        detail.status?.gitWorktreeState?.count ?? detail.target.dirtyCount
    }

    private var isDirty: Bool {
        detail.status?.gitWorktreeState?.dirty == true || detail.target.isDirty
    }

    private var blockers: [CloseoutPayload.Blocker] {
        detail.closeout?.claimBlockers ?? []
    }

    private var nextAction: CloseoutPayload.NextAction? {
        detail.closeout?.nextAction
    }

    private var driftWarns: Bool {
        detail.status?.kitDrift?.hasWarning == true
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(title, systemImage: systemImage)
                .font(.headline)
            Text(message)
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)

            HStack(spacing: 8) {
                if isDirty || !blockers.isEmpty {
                    Button {
                        store.requestCloseoutFixConfirmation()
                    } label: {
                        Label("Run Guided Closeout", systemImage: "wand.and.stars")
                    }
                    .disabled(store.selectedTarget == nil || store.isRunningCloseoutFix)
                }

                if let command = nextAction?.command {
                    Button {
                        store.copy(command)
                    } label: {
                        Label("Copy Next Command", systemImage: "doc.on.doc")
                    }
                }

                if driftWarns {
                    Button {
                        store.previewSelectedTargetUpdate()
                    } label: {
                        Label("Preview Target Update", systemImage: "doc.text.magnifyingglass")
                    }
                }
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(nsColor: .controlBackgroundColor), in: RoundedRectangle(cornerRadius: 8))
        .overlay {
            RoundedRectangle(cornerRadius: 8)
                .stroke(Color(nsColor: .separatorColor), lineWidth: 0.5)
        }
    }

    private var title: String {
        if isDirty {
            return "Dirty repo closeout"
        }
        if !blockers.isEmpty {
            return "Closeout blockers"
        }
        if driftWarns {
            return "Kit update available"
        }
        if detail.closeout?.canClaimDone == true {
            return "Ready to claim done"
        }
        return "Review next command"
    }

    private var message: String {
        if isDirty {
            return "\(dirtyCount) changed file\(dirtyCount == 1 ? "" : "s") reported. Guided closeout is available after confirmation."
        }
        if let blocker = blockers.first {
            return blocker.message ?? blocker.code ?? "Closeout has blockers."
        }
        if driftWarns {
            return detail.status?.kitDrift?.reason ?? "Preview the target update before applying it in Terminal."
        }
        if detail.closeout?.canClaimDone == true {
            return "No dirty files or closeout blockers are reported for this target."
        }
        return nextAction?.reason ?? "Use the next command list to continue."
    }

    private var systemImage: String {
        if isDirty || !blockers.isEmpty {
            return "exclamationmark.triangle.fill"
        }
        if driftWarns {
            return "arrow.triangle.2.circlepath"
        }
        if detail.closeout?.canClaimDone == true {
            return "checkmark.seal.fill"
        }
        return "arrow.right.circle.fill"
    }
}

private struct BlockersPanel: View {
    let blockers: [CloseoutPayload.Blocker]

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Blockers")
                .font(.headline)
            ForEach(blockers) { blocker in
                HStack(alignment: .top, spacing: 8) {
                    Image(systemName: "exclamationmark.circle")
                        .foregroundStyle(.orange)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(blocker.code ?? "blocker")
                            .font(.callout.weight(.semibold))
                        Text(blocker.message ?? "")
                            .foregroundStyle(.secondary)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
            }
        }
    }
}

private struct NextCommandsPanel: View {
    @ObservedObject var store: KitCompanionStore
    let steps: [StartPayload.NextStep]

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Next Commands")
                .font(.headline)

            if steps.isEmpty {
                Text("No next commands returned.")
                    .foregroundStyle(.secondary)
            } else {
                ForEach(steps.prefix(4)) { step in
                    HStack(spacing: 10) {
                        VStack(alignment: .leading, spacing: 2) {
                            Text(step.label ?? "Command")
                                .font(.callout.weight(.semibold))
                            Text(step.command ?? "")
                                .font(.caption.monospaced())
                                .foregroundStyle(.secondary)
                                .lineLimit(1)
                                .truncationMode(.middle)
                        }
                        Spacer()
                        Button {
                            store.copy(step.command)
                        } label: {
                            Image(systemName: "doc.on.doc")
                        }
                        .help("Copy command")
                    }
                    .padding(.vertical, 4)
                }
            }
        }
    }
}

private struct CloseoutFixJobView: View {
    let payload: CloseoutFixPayload?
    let events: [CloseoutFixEvent]
    let isRunning: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("Closeout Fix")
                    .font(.headline)
                if isRunning {
                    ProgressView()
                        .controlSize(.small)
                }
                Spacer()
                Text(payload?.result ?? "running")
                    .foregroundStyle(payload?.result == "applied" ? .green : .secondary)
            }

            if let jobDir = payload?.jobDir {
                Text(KitDisplay.shortPath(jobDir))
                    .font(.caption.monospaced())
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
                    .truncationMode(.middle)
            }

            ForEach(events.suffix(4)) { event in
                Text(event.displayText)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }

            if let commits = payload?.commits, !commits.isEmpty {
                Text("Commits")
                    .font(.subheadline.weight(.semibold))
                ForEach(commits.prefix(5)) { commit in
                    Text("\(commit.shortSha ?? "") \(commit.subject ?? "commit")")
                        .font(.caption.monospaced())
                        .lineLimit(1)
                }
            }

            if let pushes = payload?.branchesPushed, !pushes.isEmpty {
                Text("Pushes")
                    .font(.subheadline.weight(.semibold))
                ForEach(pushes) { push in
                    Text("\(push.branch ?? "branch"): \(push.exitCode == 0 ? "pushed" : "blocked")")
                        .font(.caption)
                        .foregroundStyle(push.exitCode == 0 ? .green : .orange)
                }
            }

            if let worktrees = payload?.worktreesPruned, !worktrees.isEmpty {
                Text("Pruned Worktrees")
                    .font(.subheadline.weight(.semibold))
                ForEach(worktrees.prefix(5)) { worktree in
                    Text(KitDisplay.shortPath(worktree.path ?? "worktree"))
                        .font(.caption.monospaced())
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                        .truncationMode(.middle)
                }
            }

            if let receipts = payload?.receipts, !receipts.isEmpty {
                Text("Receipts")
                    .font(.subheadline.weight(.semibold))
                ForEach(receipts.prefix(5)) { receipt in
                    Text(KitDisplay.shortPath(receipt.path ?? "receipt"))
                        .font(.caption.monospaced())
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                        .truncationMode(.middle)
                }
            }

            if let blockers = payload?.blockers, !blockers.isEmpty {
                Text("Blockers")
                    .font(.subheadline.weight(.semibold))
                ForEach(blockers.prefix(5), id: \.self) { blocker in
                    Text(blocker)
                        .font(.caption)
                        .foregroundStyle(.orange)
                        .lineLimit(2)
                }
            }
        }
    }
}

struct UpdatePreviewView: View {
    let preview: UpdatePreviewPayload

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Update Preview")
                .font(.headline)
            Text("\(preview.targets?.count ?? 0) target results")
                .foregroundStyle(.secondary)
            ForEach((preview.targets ?? []).prefix(5)) { target in
                Text("\(target.name ?? target.repo ?? "target"): \(target.status ?? "unknown")")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
    }
}
