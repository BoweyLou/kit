import SwiftUI

struct CommandBrowserView: View {
    @ObservedObject var store: KitCompanionStore

    var body: some View {
        HStack(alignment: .top, spacing: 16) {
            VStack(alignment: .leading, spacing: 10) {
                TextField("Search commands", text: $store.commandSearch)
                    .textFieldStyle(.roundedBorder)

                List(selection: $store.selectedCommandID) {
                    ForEach(store.filteredCommands) { command in
                        CommandRow(command: command)
                            .tag(command.id)
                            .onTapGesture {
                                store.selectCommand(command)
                            }
                    }
                }
                .frame(minWidth: 280, idealWidth: 320)
            }

            Divider()

            CommandDetailView(store: store, command: store.selectedCommand)
                .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        }
        .onAppear {
            if store.commandMap == nil {
                store.loadCommandMap()
            }
        }
    }
}

private struct CommandRow: View {
    let command: CommandEntry

    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            HStack(spacing: 6) {
                Image(systemName: command.appCoverage.systemImage)
                    .foregroundStyle(.secondary)
                Text(command.displayName)
                    .font(.body.monospaced())
                    .lineLimit(1)
                Spacer()
            }
            Text(command.summary ?? command.mutation)
                .font(.caption)
                .foregroundStyle(.secondary)
                .lineLimit(2)
            HStack(spacing: 6) {
                CommandBadge(label: command.appCoverage.label, systemImage: command.appCoverage.systemImage)
                if command.isAgentFocused {
                    CommandBadge(label: "Agent", systemImage: "gearshape.2")
                }
            }
        }
        .padding(.vertical, 4)
    }
}

private struct CommandDetailView: View {
    @ObservedObject var store: KitCompanionStore
    let command: CommandEntry?

    var body: some View {
        if let command {
            VStack(alignment: .leading, spacing: 14) {
                HStack(alignment: .firstTextBaseline, spacing: 8) {
                    Text(command.displayName)
                        .font(.title3.weight(.semibold).monospaced())
                    CommandBadge(label: command.appCoverage.label, systemImage: command.appCoverage.systemImage)
                    if command.isAgentFocused {
                        CommandBadge(label: "Agent", systemImage: "gearshape.2")
                    }
                    Spacer()
                }

                Text(command.summary ?? "No summary provided.")
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)

                Grid(alignment: .leading, horizontalSpacing: 16, verticalSpacing: 8) {
                    GridRow {
                        Text("Mutation").foregroundStyle(.secondary)
                        Text(command.mutation)
                    }
                    GridRow {
                        Text("Target write").foregroundStyle(.secondary)
                        Text(command.targetRepoWrite)
                    }
                    GridRow {
                        Text("Sidecar write").foregroundStyle(.secondary)
                        Text(command.sidecarWrite)
                    }
                    GridRow {
                        Text("JSON").foregroundStyle(.secondary)
                        Text(command.jsonSupported ? "supported" : "not supported")
                    }
                    GridRow {
                        Text("Schema").foregroundStyle(.secondary)
                        Text(command.outputSchema ?? "none")
                    }
                }
                .font(.callout.monospacedDigit())

                HStack(spacing: 10) {
                    Button {
                        store.runCommand(command)
                    } label: {
                        Label(runLabel(for: command), systemImage: command.safeRunKind == .preview ? "doc.text.magnifyingglass" : "play.fill")
                    }
                    .disabled(command.safeArguments(selectedRepo: store.selectedTarget?.root) == nil || store.isRunningCommand)

                    Button {
                        store.copyCommand(command)
                    } label: {
                        Label("Copy", systemImage: "doc.on.doc")
                    }

                    Button {
                        store.openTerminal(for: command)
                    } label: {
                        Label("Terminal", systemImage: "terminal")
                    }
                }

                if command.requiresSelectedRepo, store.selectedTarget == nil {
                    Label("Select a target repo to run this command in the app.", systemImage: "folder.badge.questionmark")
                        .foregroundStyle(.secondary)
                }

                VStack(alignment: .leading, spacing: 6) {
                    Text("Terminal Command")
                        .font(.headline)
                    Text(command.terminalCommand(selectedRepo: store.selectedTarget?.root))
                        .font(.caption.monospaced())
                        .textSelection(.enabled)
                        .lineLimit(3)
                        .padding(8)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(.quaternary.opacity(0.55), in: RoundedRectangle(cornerRadius: 6))
                }

                if let output = store.commandOutput, !output.isEmpty {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("Output")
                            .font(.headline)
                        ScrollView {
                            Text(output)
                                .font(.caption.monospaced())
                                .textSelection(.enabled)
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                        .frame(minHeight: 140)
                    }
                }

                Spacer(minLength: 0)
            }
        } else if store.isLoadingCommandMap {
            ProgressView("Loading commands")
        } else {
            ContentUnavailableView("No commands", systemImage: "terminal")
        }
    }

    private func runLabel(for command: CommandEntry) -> String {
        switch command.safeRunKind {
        case .preview:
            return "Preview"
        case .readOnly:
            return "Run"
        case nil:
            return "Run"
        }
    }
}

struct CommandBadge: View {
    let label: String
    let systemImage: String

    var body: some View {
        Label(label, systemImage: systemImage)
            .font(.caption2.weight(.medium))
            .labelStyle(.titleAndIcon)
            .padding(.horizontal, 6)
            .padding(.vertical, 3)
            .background(.quaternary.opacity(0.65), in: RoundedRectangle(cornerRadius: 6))
    }
}
