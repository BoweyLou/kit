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
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 260), spacing: 12)], alignment: .leading, spacing: 12) {
                ForEach(commands) { command in
                    WorkflowCommandTile(store: store, command: command)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)

            if mode == .batch, let preview = store.updatePreview {
                UpdatePreviewView(preview: preview)
                    .padding(.top, 14)
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
