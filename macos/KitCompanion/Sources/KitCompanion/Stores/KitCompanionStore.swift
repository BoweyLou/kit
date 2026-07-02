import AppKit
import Foundation

enum KitSettingsKeys {
    static let kitBinaryPath = "kitBinaryPath"
    static let automaticallyCheckForUpdates = "automaticallyCheckForUpdates"
}

enum KitSettings {
    static func defaultKitBinaryPath() -> String {
        NSHomeDirectory() + "/.local/bin/kit"
    }

    static func kitBinaryPath() -> String {
        let stored = UserDefaults.standard.string(forKey: KitSettingsKeys.kitBinaryPath) ?? ""
        return stored.isEmpty ? defaultKitBinaryPath() : stored
    }
}

enum DashboardSection: String, CaseIterable, Identifiable {
    case overview
    case commands
    case workflows
    case batch

    var id: String { rawValue }

    var label: String {
        switch self {
        case .overview:
            return "Overview"
        case .commands:
            return "Commands"
        case .workflows:
            return "Workflows"
        case .batch:
            return "Batch"
        }
    }
}

@MainActor
final class KitCompanionStore: ObservableObject {
    @Published var targets: [KitTarget] = []
    @Published var selectedTargetID: String?
    @Published var detail: RepoDetail?
    @Published var updatePreview: UpdatePreviewPayload?
    @Published var closeoutFixPayload: CloseoutFixPayload?
    @Published var closeoutFixEvents: [CloseoutFixEvent] = []
    @Published var commandMap: CommandMapPayload?
    @Published var selectedCommandID: String?
    @Published var commandScope: CommandBrowserScope = .recommended
    @Published var commandSearch = ""
    @Published var commandOutput: String?
    @Published var dashboardSection: DashboardSection = .overview
    @Published var isRefreshing = false
    @Published var isLoadingDetail = false
    @Published var isLoadingCommandMap = false
    @Published var isRunningCommand = false
    @Published var isRunningCloseoutFix = false
    @Published var isConfirmingCloseoutFix = false
    @Published var lastRefresh: Date?
    @Published var isCheckingForUpdates = false
    @Published var message: String?
    @Published var errorMessage: String?

    private let runner: KitProcessRunner
    private let updateService: SparkleUpdateService
    private var detailLoadGeneration = 0

    init(runner: KitProcessRunner = KitProcessRunner(), updateService: SparkleUpdateService? = nil) {
        self.runner = runner
        self.updateService = updateService ?? .shared
        if UserDefaults.standard.object(forKey: KitSettingsKeys.automaticallyCheckForUpdates) == nil {
            UserDefaults.standard.set(true, forKey: KitSettingsKeys.automaticallyCheckForUpdates)
        }
        self.updateService.setAutomaticallyChecksForUpdates(UserDefaults.standard.bool(forKey: KitSettingsKeys.automaticallyCheckForUpdates))
    }

    var selectedTarget: KitTarget? {
        targets.first { $0.id == selectedTargetID } ?? targets.first
    }

    var visibleCommands: [CommandEntry] {
        commandMap?.visibleCommands ?? []
    }

    var scopedCommands: [CommandEntry] {
        visibleCommands
            .filter { commandScope.includes($0) }
            .sorted { lhs, rhs in
                if lhs.commandBrowserRank != rhs.commandBrowserRank {
                    return lhs.commandBrowserRank < rhs.commandBrowserRank
                }
                return lhs.displayName.localizedCaseInsensitiveCompare(rhs.displayName) == .orderedAscending
            }
    }

    var filteredCommands: [CommandEntry] {
        scopedCommands.filter { $0.matches(commandSearch) }
    }

    var selectedCommand: CommandEntry? {
        if let selectedCommandID,
           let command = filteredCommands.first(where: { $0.id == selectedCommandID }) {
            return command
        }
        return filteredCommands.first
    }

    var dirtyCount: Int {
        targets.filter(\.isDirty).count
    }

    var menuTitle: String {
        if targets.isEmpty {
            return "kit"
        }
        if dirtyCount > 0 {
            return "kit \(dirtyCount)"
        }
        return "kit OK"
    }

    var menuSymbolName: String {
        if errorMessage != nil {
            return "exclamationmark.triangle"
        }
        if dirtyCount > 0 {
            return "circle.grid.cross"
        }
        return "checkmark.circle"
    }

    func refreshTargets() {
        guard !isRefreshing else {
            return
        }
        isRefreshing = true
        errorMessage = nil
        message = "Refreshing targets"

        Task {
            do {
                let payload = try await runner.runJSON(
                    TargetReportPayload.self,
                    arguments: ["target", "dirty-report", "--json"],
                    kitPath: KitSettings.kitBinaryPath()
                )
                targets = payload.targets.sorted { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
                if selectedTargetID == nil {
                    selectedTargetID = targets.first?.id
                } else if let selectedTargetID, !targets.contains(where: { $0.id == selectedTargetID }) {
                    self.selectedTargetID = targets.first?.id
                }
                lastRefresh = Date()
                message = "\(targets.count) target repos, \(dirtyCount) dirty"
                if let selectedTarget {
                    loadDetail(for: selectedTarget)
                }
                if commandMap == nil {
                    loadCommandMap()
                }
            } catch {
                errorMessage = error.localizedDescription
                message = nil
            }
            isRefreshing = false
        }
    }

    func select(_ target: KitTarget) {
        selectTargetID(target.id)
    }

    func selectTargetID(_ targetID: String?) {
        if selectedTargetID == targetID {
            if detail == nil, let target = targets.first(where: { $0.id == targetID }) {
                loadDetail(for: target)
            }
            return
        }

        selectedTargetID = targetID
        detail = nil
        updatePreview = nil
        isConfirmingCloseoutFix = false
        commandOutput = nil
        if !isRunningCloseoutFix {
            closeoutFixPayload = nil
            closeoutFixEvents = []
        }

        guard let target = targets.first(where: { $0.id == targetID }) else {
            return
        }
        loadDetail(for: target)
    }

    func loadSelectedDetail() {
        guard let selectedTarget else {
            return
        }
        loadDetail(for: selectedTarget)
    }

    func loadDetail(for target: KitTarget) {
        detailLoadGeneration += 1
        let generation = detailLoadGeneration
        isLoadingDetail = true
        errorMessage = nil

        Task {
            do {
                async let status = runner.runJSON(
                    StatusPayload.self,
                    arguments: ["status", "--repo", target.root, "--json"],
                    kitPath: KitSettings.kitBinaryPath()
                )
                async let start = runner.runJSON(
                    StartPayload.self,
                    arguments: ["start", "--repo", target.root, "--no-update", "--json"],
                    kitPath: KitSettings.kitBinaryPath()
                )
                async let closeout = runner.runJSON(
                    CloseoutPayload.self,
                    arguments: ["closeout-plan", "--repo", target.root, "--json"],
                    kitPath: KitSettings.kitBinaryPath()
                )
                let loadedDetail = try await RepoDetail(target: target, status: status, start: start, closeout: closeout)
                guard generation == detailLoadGeneration, selectedTargetID == target.id else {
                    return
                }
                detail = loadedDetail
            } catch {
                guard generation == detailLoadGeneration else {
                    return
                }
                errorMessage = error.localizedDescription
            }
            guard generation == detailLoadGeneration else {
                return
            }
            isLoadingDetail = false
        }
    }

    func loadCommandMap() {
        guard !isLoadingCommandMap else {
            return
        }
        isLoadingCommandMap = true
        errorMessage = nil

        Task {
            do {
                let payload = try await runner.runJSON(
                    CommandMapPayload.self,
                    arguments: ["command-map", "--json"],
                    kitPath: KitSettings.kitBinaryPath()
                )
                commandMap = payload
                if selectedCommandID == nil {
                    selectedCommandID = payload.visibleCommands(in: commandScope).first?.id ?? payload.visibleCommands.first?.id
                }
            } catch {
                errorMessage = error.localizedDescription
            }
            isLoadingCommandMap = false
        }
    }

    func selectCommand(_ command: CommandEntry) {
        selectedCommandID = command.id
        commandOutput = nil
    }

    func selectCommandScope(_ scope: CommandBrowserScope) {
        commandScope = scope
        if let selectedCommandID,
           filteredCommands.contains(where: { $0.id == selectedCommandID }) {
            return
        }
        selectedCommandID = filteredCommands.first?.id
        commandOutput = nil
    }

    func runCommand(_ command: CommandEntry? = nil) {
        let command = command ?? selectedCommand
        guard let command else {
            return
        }
        guard let arguments = command.safeArguments(selectedRepo: selectedTarget?.root) else {
            copyCommand(command)
            return
        }

        isRunningCommand = true
        errorMessage = nil
        commandOutput = nil
        message = "Running \(command.displayName)"

        Task {
            do {
                commandOutput = try await runner.runJSONText(
                    arguments: arguments,
                    kitPath: KitSettings.kitBinaryPath(),
                    workingDirectory: selectedTarget?.root
                )
                message = "Finished \(command.displayName)"
            } catch {
                errorMessage = error.localizedDescription
                message = nil
            }
            isRunningCommand = false
        }
    }

    func runCloseoutFix() {
        guard let selectedTarget else {
            return
        }
        guard !isRunningCloseoutFix else {
            return
        }

        isConfirmingCloseoutFix = false
        isRunningCloseoutFix = true
        closeoutFixPayload = nil
        closeoutFixEvents = []
        errorMessage = nil
        message = "Running closeout fix"

        Task {
            do {
                let payload = try await runner.runCloseoutFix(
                    arguments: ["closeout-fix", "--repo", selectedTarget.root, "--apply", "--jsonl"],
                    kitPath: KitSettings.kitBinaryPath(),
                    workingDirectory: selectedTarget.root
                ) { event in
                    Task { @MainActor in
                        self.closeoutFixEvents.append(event)
                    }
                }
                closeoutFixPayload = payload
                message = payload.result == "applied" ? "Closeout fix applied" : "Closeout fix blocked"
                loadDetail(for: selectedTarget)
                refreshTargets()
            } catch {
                errorMessage = error.localizedDescription
                message = nil
            }
            isRunningCloseoutFix = false
        }
    }

    func requestCloseoutFixConfirmation() {
        guard selectedTarget != nil, !isRunningCloseoutFix else {
            return
        }
        isConfirmingCloseoutFix = true
    }

    func copyCommand(_ command: CommandEntry? = nil) {
        let command = command ?? selectedCommand
        guard let command else {
            return
        }
        copy(command.terminalCommand(selectedRepo: selectedTarget?.root))
    }

    func openTerminal(for command: CommandEntry? = nil) {
        copyCommand(command)
        let root = selectedTarget?.root ?? NSHomeDirectory()
        let url = URL(fileURLWithPath: root, isDirectory: true)
        NSWorkspace.shared.open([url], withApplicationAt: URL(fileURLWithPath: "/System/Applications/Utilities/Terminal.app"), configuration: NSWorkspace.OpenConfiguration())
        message = "Copied command and opened Terminal"
    }

    func previewBatchUpdate() {
        errorMessage = nil
        message = "Previewing batch update"
        Task {
            do {
                updatePreview = try await runner.runJSON(
                    UpdatePreviewPayload.self,
                    arguments: ["update", "--all", "--dry-run", "--json"],
                    kitPath: KitSettings.kitBinaryPath()
                )
                message = "Update preview complete"
            } catch {
                errorMessage = error.localizedDescription
                message = nil
            }
        }
    }

    func previewSelectedTargetUpdate() {
        guard let selectedTarget else {
            previewBatchUpdate()
            return
        }
        errorMessage = nil
        message = "Previewing target update"
        Task {
            do {
                updatePreview = try await runner.runJSON(
                    UpdatePreviewPayload.self,
                    arguments: ["update", "--repo", selectedTarget.root, "--dry-run", "--json"],
                    kitPath: KitSettings.kitBinaryPath(),
                    workingDirectory: selectedTarget.root
                )
                message = "Target update preview complete"
            } catch {
                errorMessage = error.localizedDescription
                message = nil
            }
        }
    }

    func checkForUpdates(silent: Bool = false) {
        if !silent {
            message = "Opening app update checker"
            errorMessage = nil
            updateService.checkForUpdates()
        } else {
            updateService.checkForUpdatesInBackground()
        }
    }

    func openSelectedInFinder() {
        guard let selectedTarget else {
            return
        }
        NSWorkspace.shared.open(URL(fileURLWithPath: selectedTarget.root, isDirectory: true))
    }

    func openSelectedInTerminal() {
        guard let selectedTarget else {
            return
        }
        let url = URL(fileURLWithPath: selectedTarget.root, isDirectory: true)
        NSWorkspace.shared.open([url], withApplicationAt: URL(fileURLWithPath: "/System/Applications/Utilities/Terminal.app"), configuration: NSWorkspace.OpenConfiguration())
    }

    func copy(_ command: String?) {
        guard let command, !command.isEmpty else {
            return
        }
        NSPasteboard.general.clearContents()
        NSPasteboard.general.setString(command, forType: .string)
        message = "Copied command"
    }
}
