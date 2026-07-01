import SwiftUI

struct CommandBrowserView: View {
    @ObservedObject var store: KitCompanionStore

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Picker("Scope", selection: Binding(
                get: { store.commandScope },
                set: { store.selectCommandScope($0) }
            )) {
                ForEach(CommandBrowserScope.allCases) { scope in
                    Text(scope.label).tag(scope)
                }
            }
            .pickerStyle(.segmented)

            HStack(alignment: .top, spacing: 16) {
                VStack(alignment: .leading, spacing: 10) {
                    TextField("Search \(store.commandScope.label.lowercased()) commands", text: $store.commandSearch)
                        .textFieldStyle(.roundedBorder)

                    if store.filteredCommands.isEmpty {
                        ContentUnavailableView("No commands", systemImage: store.commandScope.systemImage)
                            .frame(minWidth: 280, idealWidth: 320, maxHeight: .infinity)
                    } else {
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
                }

                Divider()

                CommandDetailView(store: store, command: store.selectedCommand)
                    .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
            }
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
                if command.safeRunKind == .readOnly {
                    CommandBadge(label: "Read-only", systemImage: "checkmark.shield")
                }
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
            ScrollView {
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

                    if command.isAgentFocused {
                        Label("Agent-facing command", systemImage: "gearshape.2")
                            .foregroundStyle(.secondary)
                    }

                    Text(command.summary ?? "No summary provided.")
                        .foregroundStyle(.secondary)
                        .fixedSize(horizontal: false, vertical: true)

                    CommandImpactGrid(command: command)

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

                    DisclosureGroup("Terminal Command") {
                        Text(command.terminalCommand(selectedRepo: store.selectedTarget?.root))
                            .font(.caption.monospaced())
                            .textSelection(.enabled)
                            .lineLimit(4)
                            .padding(8)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(.quaternary.opacity(0.55), in: RoundedRectangle(cornerRadius: 6))
                    }

                    if let output = store.commandOutput, !output.isEmpty {
                        CommandOutputSummaryView(output: output)

                        DisclosureGroup("Raw Output") {
                            ScrollView {
                                Text(output)
                                    .font(.caption.monospaced())
                                    .textSelection(.enabled)
                                    .frame(maxWidth: .infinity, alignment: .leading)
                            }
                            .frame(minHeight: 140)
                        }
                    }
                }
                .frame(maxWidth: .infinity, alignment: .topLeading)
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

private struct CommandImpactGrid: View {
    let command: CommandEntry

    var body: some View {
        Grid(alignment: .leading, horizontalSpacing: 16, verticalSpacing: 8) {
            GridRow {
                Text("App action").foregroundStyle(.secondary)
                Text(command.appCoverage.label)
            }
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
        }
        .font(.callout.monospacedDigit())
    }
}

private struct CommandOutputSummaryView: View {
    let output: String

    private var summary: CommandOutputSummary {
        CommandOutputSummary(output)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(summary.title)
                .font(.headline)
            Text(summary.subtitle)
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)
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

private struct CommandOutputSummary {
    let title: String
    let subtitle: String

    init(_ output: String) {
        guard let data = output.data(using: .utf8),
              let object = try? JSONSerialization.jsonObject(with: data),
              let dictionary = object as? [String: Any] else {
            title = "Command output"
            subtitle = "\(output.count) characters returned"
            return
        }

        let command = dictionary.stringValue("command") ?? "Command"
        let status = dictionary.stringValue("status")
            ?? dictionary.stringValue("result")
            ?? dictionary.stringValue("completion_state")
            ?? dictionary.stringValue("mode")
        let exitCode = dictionary.intValue("exit_code")
        let targetCount = (dictionary["targets"] as? [Any])?.count

        title = command

        var parts: [String] = []
        if let status {
            parts.append(status)
        }
        if let exitCode {
            parts.append("exit \(exitCode)")
        }
        if let targetCount {
            parts.append("\(targetCount) target\(targetCount == 1 ? "" : "s")")
        }
        subtitle = parts.isEmpty ? "JSON output returned." : parts.joined(separator: " · ")
    }
}

private extension Dictionary where Key == String, Value == Any {
    func stringValue(_ key: String) -> String? {
        self[key] as? String
    }

    func intValue(_ key: String) -> Int? {
        self[key] as? Int
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
