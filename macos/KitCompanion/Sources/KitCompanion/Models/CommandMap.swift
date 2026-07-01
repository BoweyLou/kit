import Foundation

struct CommandMapPayload: Codable {
    struct CLI: Codable {
        let name: String?
        let version: String?
        let invocation: String?
        let entrypoint: String?
    }

    let cli: CLI?
    let commands: [CommandEntry]

    var visibleCommands: [CommandEntry] {
        commands
            .filter { !$0.path.isEmpty }
            .sorted { lhs, rhs in
                lhs.displayName.localizedCaseInsensitiveCompare(rhs.displayName) == .orderedAscending
            }
    }

    func visibleCommands(in scope: CommandBrowserScope) -> [CommandEntry] {
        visibleCommands.filter { scope.includes($0) }
    }
}

struct CommandFlag: Codable, Hashable {
    let option: String?
    let dest: String?
    let help: String?
    let required: Bool?
    let choices: [String]?
}

struct CommandEntry: Codable, Identifiable, Hashable {
    let name: String
    let path: [String]
    let summary: String?
    let audience: [String]
    let mutation: String
    let targetRepoWrite: String
    let sidecarWrite: String
    let jsonSupported: Bool
    let routeRole: String?
    let canonicalCommand: String?
    let aliasOf: String?
    let outputSchema: String?
    let examples: [String]
    let flags: [CommandFlag]
    let docs: [String]

    enum CodingKeys: String, CodingKey {
        case name
        case path
        case summary
        case audience
        case mutation
        case targetRepoWrite = "target_repo_write"
        case sidecarWrite = "sidecar_write"
        case jsonSupported = "json_supported"
        case routeRole = "route_role"
        case canonicalCommand = "canonical_command"
        case aliasOf = "alias_of"
        case outputSchema = "output_schema"
        case examples
        case flags
        case docs
    }

    var id: String {
        displayName
    }

    var displayName: String {
        path.joined(separator: " ")
    }

    var isAgentFocused: Bool {
        audience == ["agent"] || routeRole == "agent-only"
    }

    var requiresSelectedRepo: Bool {
        switch displayName {
        case "target import", "worktree prune":
            return true
        case "update":
            return false
        default:
            return hasFlag("--repo")
        }
    }

    var supportsInAppRun: Bool {
        safeRunKind != nil
    }

    var safeRunKind: CommandRunKind? {
        guard jsonSupported else {
            return nil
        }

        switch displayName {
        case "start",
             "closeout-fix",
             "update",
             "target import",
             "target prune-missing",
             "target repair-source-clone",
             "target update",
             "target update-all",
             "worktree prune",
             "automation-handoff",
             "agent-self-heal":
            return .preview
        default:
            break
        }

        let writesTargetOnlyWhenFlagged = targetRepoWrite == "never" || targetRepoWrite == "with --write"
        let writesSidecarOnlyWhenFlagged = sidecarWrite == "never" || sidecarWrite == "optional"
        if mutation == "read-only", writesTargetOnlyWhenFlagged, writesSidecarOnlyWhenFlagged {
            return .readOnly
        }

        return nil
    }

    var appCoverage: CommandCoverage {
        if ["target dirty-report", "status", "start", "closeout-plan", "closeout-fix", "update"].contains(displayName) {
            return .native
        }
        if safeRunKind == .readOnly {
            return .runInApp
        }
        if safeRunKind == .preview {
            return .previewInApp
        }
        if jsonSupported || !path.isEmpty {
            return .terminalHandoff
        }
        return .unsupported
    }

    var commandBrowserRank: Int {
        if CommandBrowserScope.recommendedCommandNames.contains(displayName) {
            return 0
        }
        if appCoverage == .native {
            return 1
        }
        if safeRunKind == .readOnly {
            return 2
        }
        if safeRunKind == .preview {
            return 3
        }
        if isAgentFocused {
            return 5
        }
        return 4
    }

    func matches(_ query: String) -> Bool {
        let trimmed = query.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else {
            return true
        }
        let haystack = [
            displayName,
            summary ?? "",
            mutation,
            audience.joined(separator: " "),
            outputSchema ?? ""
        ].joined(separator: " ").localizedLowercase
        return haystack.contains(trimmed.localizedLowercase)
    }

    func safeArguments(selectedRepo: String?) -> [String]? {
        guard let safeRunKind else {
            return nil
        }

        var args = path
        func appendJSON() {
            if hasFlag("--json"), !args.contains("--json") {
                args.append("--json")
            }
        }
        func appendRepo() -> Bool {
            guard hasFlag("--repo") else {
                return true
            }
            guard let selectedRepo else {
                return false
            }
            args.append(contentsOf: ["--repo", selectedRepo])
            return true
        }
        func appendRoot() -> Bool {
            guard hasFlag("--root") else {
                return true
            }
            guard let selectedRepo else {
                return false
            }
            args.append(contentsOf: ["--root", selectedRepo])
            return true
        }

        switch displayName {
        case "start":
            guard appendRepo() else {
                return nil
            }
            args.append("--no-update")
            appendJSON()
        case "closeout-fix":
            guard appendRepo() else {
                return nil
            }
            appendJSON()
        case "update":
            if let selectedRepo {
                args.append(contentsOf: ["--repo", selectedRepo])
            } else {
                args.append("--all")
            }
            args.append("--dry-run")
            appendJSON()
        case "target import", "worktree prune":
            guard appendRoot() else {
                return nil
            }
            args.append("--dry-run")
            appendJSON()
        case "target prune-missing", "target update-all":
            args.append("--dry-run")
            appendJSON()
        case "target update":
            guard appendRepo() else {
                return nil
            }
            args.append("--dry-run")
            appendJSON()
        case "target repair-source-clone", "agent-self-heal":
            guard appendRepo() else {
                return nil
            }
            appendJSON()
        case "automation-handoff":
            guard appendRepo() else {
                return nil
            }
            args.append("--dry-run")
            appendJSON()
        default:
            guard safeRunKind == .readOnly, appendRepo() else {
                return nil
            }
            appendJSON()
        }

        return args
    }

    func terminalCommand(selectedRepo: String?) -> String {
        if let safeArguments = safeArguments(selectedRepo: selectedRepo) {
            return KitCommandLine.render(arguments: safeArguments)
        }
        if let example = examples.first, !example.isEmpty {
            return example
        }

        var args = path
        if hasFlag("--repo"), let selectedRepo {
            args.append(contentsOf: ["--repo", selectedRepo])
        }
        if hasFlag("--root"), let selectedRepo {
            args.append(contentsOf: ["--root", selectedRepo])
        }
        return KitCommandLine.render(arguments: args)
    }

    private func hasFlag(_ option: String) -> Bool {
        flags.contains { $0.option == option }
    }
}

enum CommandRunKind: String {
    case readOnly
    case preview
}

enum CommandBrowserScope: String, CaseIterable, Identifiable {
    case recommended
    case readOnly
    case preview
    case terminal
    case agentTools

    static let recommendedCommandNames: Set<String> = [
        "start",
        "status",
        "doctor",
        "mode-check",
        "goal-check",
        "backlog-status",
        "branch-readiness",
        "closeout-plan",
        "doc-impact",
        "verify",
        "worktree audit",
        "target dirty-report",
        "target list",
        "update"
    ]

    var id: String { rawValue }

    var label: String {
        switch self {
        case .recommended:
            return "Recommended"
        case .readOnly:
            return "Read-only"
        case .preview:
            return "Previews"
        case .terminal:
            return "Terminal"
        case .agentTools:
            return "Agent"
        }
    }

    var systemImage: String {
        switch self {
        case .recommended:
            return "star"
        case .readOnly:
            return "checkmark.shield"
        case .preview:
            return "doc.text.magnifyingglass"
        case .terminal:
            return "terminal"
        case .agentTools:
            return "gearshape.2"
        }
    }

    func includes(_ command: CommandEntry) -> Bool {
        switch self {
        case .recommended:
            return !command.isAgentFocused
                && (Self.recommendedCommandNames.contains(command.displayName) || command.appCoverage == .native)
        case .readOnly:
            return !command.isAgentFocused && command.safeRunKind == .readOnly
        case .preview:
            return !command.isAgentFocused && command.safeRunKind == .preview
        case .terminal:
            return !command.isAgentFocused && command.appCoverage == .terminalHandoff
        case .agentTools:
            return command.isAgentFocused
        }
    }
}

enum CommandCoverage: String, CaseIterable {
    case native
    case runInApp
    case previewInApp
    case terminalHandoff
    case unsupported

    var label: String {
        switch self {
        case .native:
            return "Native"
        case .runInApp:
            return "Run"
        case .previewInApp:
            return "Preview"
        case .terminalHandoff:
            return "Terminal"
        case .unsupported:
            return "Reference"
        }
    }

    var systemImage: String {
        switch self {
        case .native:
            return "rectangle.3.group"
        case .runInApp:
            return "play.circle"
        case .previewInApp:
            return "doc.text.magnifyingglass"
        case .terminalHandoff:
            return "terminal"
        case .unsupported:
            return "book"
        }
    }
}

enum KitCommandLine {
    static func render(arguments: [String]) -> String {
        (["kit"] + arguments).map(shellQuote).joined(separator: " ")
    }

    static func shellQuote(_ value: String) -> String {
        if value.range(of: #"[^A-Za-z0-9_@%+=:,./-]"#, options: .regularExpression) == nil {
            return value
        }
        return "'" + value.replacingOccurrences(of: "'", with: "'\\''") + "'"
    }
}
