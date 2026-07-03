import SwiftUI

struct WorkflowPanelsView: View {
    @ObservedObject var store: KitCompanionStore
    let mode: WorkflowPanelMode

    private var commands: [CommandEntry] {
        mode.commandNames.compactMap { name in
            store.visibleCommands.first { $0.displayName == name }
        }
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Label(mode.title, systemImage: mode.systemImage)
                        .font(.headline)
                    Spacer()
                    if mode == .batch {
                        Button {
                            store.previewBatchUpdate()
                        } label: {
                            Label("Preview All Targets", systemImage: "doc.text.magnifyingglass")
                        }
                    }
                }

                LazyVGrid(columns: [GridItem(.adaptive(minimum: 260), spacing: 12)], alignment: .leading, spacing: 12) {
                    ForEach(commands) { command in
                        WorkflowCommandTile(store: store, command: command)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)

                if mode == .batch {
                    BatchCloseoutPanel(store: store)
                    BatchWriteActionsPanel(store: store)
                }

                if !store.closeoutFixJobs.isEmpty {
                    DisclosureGroup("Guided Closeout Jobs") {
                        CloseoutJobsPanel(jobs: store.closeoutFixJobs)
                            .padding(.top, 4)
                    }
                }

                if mode == .batch, let preview = store.updatePreview {
                    UpdatePreviewView(preview: preview)
                        .padding(.top, 4)
                }

                if let output = store.commandOutput, !output.isEmpty {
                    WorkflowOutputView(output: output)
                }
            }
        }
        .onAppear {
            if store.commandMap == nil {
                store.loadCommandMap()
            }
        }
    }
}

enum WorkflowPanelMode: Equatable {
    case workflows
    case batch

    var title: String {
        switch self {
        case .workflows:
            return "Common Workflows"
        case .batch:
            return "Batch Targets"
        }
    }

    var systemImage: String {
        switch self {
        case .workflows:
            return "checklist"
        case .batch:
            return "square.stack.3d.up"
        }
    }

    var commandNames: [String] {
        switch self {
        case .workflows:
            return [
                "start",
                "status",
                "doctor",
                "backlog-status",
                "mode-check",
                "goal-check",
                "branch-readiness",
                "closeout-plan",
                "worktree audit",
                "update-plan",
                "doc-impact",
                "verify"
            ]
        case .batch:
            return [
                "target dirty-report",
                "target list",
                "target import",
                "target prune-missing",
                "target update-all",
                "update"
            ]
        }
    }
}

private struct BatchCloseoutPanel: View {
    @ObservedObject var store: KitCompanionStore

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Label("Batch Guided Closeout", systemImage: "wand.and.stars")
                    .font(.headline)
                Spacer()
                Text("\(store.batchCloseoutCandidates.count) ready")
                    .font(.caption.monospacedDigit())
                    .foregroundStyle(.secondary)
            }

            Text("Run closeout-fix for dirty target repos with two jobs at a time. Each repo keeps separate events, output, receipts, and blockers.")
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)

            Button {
                store.requestBatchCloseoutConfirmation()
            } label: {
                Label("Run Dirty Closeouts", systemImage: "play.fill")
            }
            .disabled(store.batchCloseoutCandidates.isEmpty || store.isBatchCloseoutRunning)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(nsColor: .controlBackgroundColor), in: RoundedRectangle(cornerRadius: 8))
        .overlay {
            RoundedRectangle(cornerRadius: 8)
                .stroke(Color(nsColor: .separatorColor), lineWidth: 0.5)
        }
    }
}

private struct BatchWriteActionsPanel: View {
    @ObservedObject var store: KitCompanionStore

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("Allowlisted Writes", systemImage: "lock.open")
                .font(.headline)
            Text("These buttons apply specific CLI write paths. Setup, install, global updates, self updates, custom agents, and write-sidecar commands remain Terminal handoffs.")
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)

            LazyVGrid(columns: [GridItem(.adaptive(minimum: 220), spacing: 10)], alignment: .leading, spacing: 10) {
                WriteActionButton(
                    title: "Import Targets",
                    systemImage: "tray.and.arrow.down",
                    disabled: store.selectedTarget == nil || store.isRunningWriteCommand,
                    action: store.requestTargetImportApply
                )
                WriteActionButton(
                    title: "Prune Missing",
                    systemImage: "trash",
                    disabled: store.isRunningWriteCommand,
                    action: store.requestTargetPruneMissingApply
                )
                WriteActionButton(
                    title: "Prune Worktrees",
                    systemImage: "square.stack.3d.down.right",
                    disabled: store.selectedTarget == nil || store.isRunningWriteCommand,
                    action: store.requestWorktreePruneApply
                )
                WriteActionButton(
                    title: "Update Clean Targets",
                    systemImage: "arrow.triangle.2.circlepath",
                    disabled: store.isRunningWriteCommand,
                    action: store.requestTargetUpdateAllApply
                )
            }
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(nsColor: .controlBackgroundColor), in: RoundedRectangle(cornerRadius: 8))
        .overlay {
            RoundedRectangle(cornerRadius: 8)
                .stroke(Color(nsColor: .separatorColor), lineWidth: 0.5)
        }
    }
}

private struct WriteActionButton: View {
    let title: String
    let systemImage: String
    let disabled: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Label(title, systemImage: systemImage)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .disabled(disabled)
    }
}

private struct WorkflowOutputView: View {
    let output: String

    var body: some View {
        DisclosureGroup("Latest Write Output") {
            ScrollView {
                Text(output)
                    .font(.caption.monospaced())
                    .textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
            .frame(minHeight: 120)
            .padding(.top, 4)
        }
    }
}

private struct WorkflowCommandTile: View {
    @ObservedObject var store: KitCompanionStore
    let command: CommandEntry

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 8) {
                Image(systemName: command.appCoverage.systemImage)
                    .foregroundStyle(.secondary)
                Text(command.displayName)
                    .font(.headline.monospaced())
                    .lineLimit(1)
                Spacer()
            }

            Text(command.summary ?? command.mutation)
                .font(.callout)
                .foregroundStyle(.secondary)
                .lineLimit(3)
                .frame(minHeight: 52, alignment: .topLeading)

            HStack(spacing: 8) {
                CommandBadge(label: command.appCoverage.label, systemImage: command.appCoverage.systemImage)
                if command.isAgentFocused {
                    CommandBadge(label: "Agent", systemImage: "gearshape.2")
                }
                Spacer()
            }

            HStack(spacing: 8) {
                Button {
                    store.runCommand(command)
                } label: {
                    Label(command.safeRunKind == .preview ? "Preview" : "Run", systemImage: command.safeRunKind == .preview ? "doc.text.magnifyingglass" : "play.fill")
                }
                .disabled(command.safeArguments(selectedRepo: store.selectedTarget?.root) == nil || store.isRunningCommand)

                Button {
                    store.copyCommand(command)
                } label: {
                    Image(systemName: "doc.on.doc")
                }
                .help("Copy command")

                Button {
                    store.openTerminal(for: command)
                } label: {
                    Image(systemName: "terminal")
                }
                .help("Open Terminal")
            }
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(nsColor: .controlBackgroundColor), in: RoundedRectangle(cornerRadius: 8))
        .overlay {
            RoundedRectangle(cornerRadius: 8)
                .stroke(Color(nsColor: .separatorColor), lineWidth: 0.5)
        }
    }
}
