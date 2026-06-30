import SwiftUI

struct DashboardView: View {
    @ObservedObject var store: KitCompanionStore

    var body: some View {
        NavigationSplitView {
            List(selection: $store.selectedTargetID) {
                ForEach(store.targets) { target in
                    TargetRow(target: target)
                        .tag(target.id)
                        .onTapGesture {
                            store.select(target)
                        }
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
            }
            if store.commandMap == nil {
                store.loadCommandMap()
            }
        }
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
                    RepoDetailView(store: store, detail: detail)
                    if store.isRunningCloseoutFix || store.closeoutFixPayload != nil || !store.closeoutFixEvents.isEmpty {
                        CloseoutFixJobView(payload: store.closeoutFixPayload, events: store.closeoutFixEvents, isRunning: store.isRunningCloseoutFix)
                    }
                    if let preview = store.updatePreview {
                        UpdatePreviewView(preview: preview)
                    }
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

            Spacer()
        }
        .padding(22)
    }

    private var header: some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 4) {
                Text(store.selectedTarget?.name ?? "kit")
                    .font(.title2.weight(.semibold))
                Text(store.selectedTarget.map { KitDisplay.shortPath($0.root) } ?? "Optional macOS companion")
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
            }

            Spacer()

            Picker("Section", selection: $store.dashboardSection) {
                ForEach(DashboardSection.allCases) { section in
                    Text(section.label).tag(section)
                }
            }
            .pickerStyle(.segmented)
            .frame(width: 360)

            Button {
                store.openSelectedInFinder()
            } label: {
                Label("Finder", systemImage: "folder")
            }
            .disabled(store.selectedTarget == nil)

            Button {
                store.openSelectedInTerminal()
            } label: {
                Label("Terminal", systemImage: "terminal")
            }
            .disabled(store.selectedTarget == nil)

            Button {
                store.runCloseoutFix()
            } label: {
                Label("Fix Dirty Repo", systemImage: "wand.and.stars")
            }
            .disabled(store.selectedTarget == nil || store.isRunningCloseoutFix)

            Button {
                store.previewBatchUpdate()
            } label: {
                Label("Preview", systemImage: "doc.text.magnifyingglass")
            }

            Button {
                store.checkForUpdates()
            } label: {
                Label("Update", systemImage: "arrow.down.app")
            }
        }
    }
}

private struct RepoDetailView: View {
    @ObservedObject var store: KitCompanionStore
    let detail: RepoDetail

    var body: some View {
        Grid(alignment: .leading, horizontalSpacing: 18, verticalSpacing: 10) {
            GridRow {
                Text("Worktree").foregroundStyle(.secondary)
                Text(detail.status?.gitWorktreeState?.state ?? detail.target.status)
            }
            GridRow {
                Text("Changed files").foregroundStyle(.secondary)
                Text("\(detail.status?.gitWorktreeState?.count ?? detail.target.dirtyCount)")
            }
            GridRow {
                Text("Kit drift").foregroundStyle(.secondary)
                Text(detail.status?.kitDrift?.classification ?? "unknown")
            }
            GridRow {
                Text("Journey").foregroundStyle(.secondary)
                Text(detail.start?.journey?.label ?? "unknown")
            }
            GridRow {
                Text("Mode").foregroundStyle(.secondary)
                Text(detail.start?.mode?.selected ?? "unknown")
            }
            GridRow {
                Text("Closeout").foregroundStyle(.secondary)
                Text(detail.closeout?.completionState ?? "unknown")
            }
        }
        .font(.body.monospacedDigit())

        if let blockers = detail.closeout?.claimBlockers, !blockers.isEmpty {
            VStack(alignment: .leading, spacing: 6) {
                Text("Blockers")
                    .font(.headline)
                ForEach(blockers) { blocker in
                    Text("\(blocker.code ?? "blocker"): \(blocker.message ?? "")")
                        .foregroundStyle(.secondary)
                        .lineLimit(2)
                }
            }
        }

        VStack(alignment: .leading, spacing: 8) {
            Text("Next Commands")
                .font(.headline)
            ForEach((detail.start?.nextSteps ?? []).prefix(4)) { step in
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(step.label ?? "Command")
                        Text(step.command ?? "")
                            .font(.caption.monospaced())
                            .foregroundStyle(.secondary)
                            .lineLimit(1)
                    }
                    Spacer()
                    Button {
                        store.copy(step.command)
                    } label: {
                        Image(systemName: "doc.on.doc")
                    }
                    .help("Copy command")
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
            Divider()
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
            Divider()
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
