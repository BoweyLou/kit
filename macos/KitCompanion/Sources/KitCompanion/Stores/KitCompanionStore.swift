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

@MainActor
final class KitCompanionStore: ObservableObject {
    @Published var targets: [KitTarget] = []
    @Published var selectedTargetID: String?
    @Published var detail: RepoDetail?
    @Published var updatePreview: UpdatePreviewPayload?
    @Published var isRefreshing = false
    @Published var isLoadingDetail = false
    @Published var lastRefresh: Date?
    @Published var updateCheckResult: UpdateCheckResult?
    @Published var isCheckingForUpdates = false
    @Published var message: String?
    @Published var errorMessage: String?

    private let runner: KitProcessRunner
    private let updateChecker: UpdateCheckService

    init(runner: KitProcessRunner = KitProcessRunner(), updateChecker: UpdateCheckService = UpdateCheckService()) {
        self.runner = runner
        self.updateChecker = updateChecker
        if UserDefaults.standard.object(forKey: KitSettingsKeys.automaticallyCheckForUpdates) == nil {
            UserDefaults.standard.set(true, forKey: KitSettingsKeys.automaticallyCheckForUpdates)
        }
        if UserDefaults.standard.bool(forKey: KitSettingsKeys.automaticallyCheckForUpdates) {
            checkForUpdates(silent: true)
        }
    }

    var selectedTarget: KitTarget? {
        targets.first { $0.id == selectedTargetID } ?? targets.first
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
                }
                lastRefresh = Date()
                message = "\(targets.count) target repos, \(dirtyCount) dirty"
                if let selectedTarget {
                    loadDetail(for: selectedTarget)
                }
            } catch {
                errorMessage = error.localizedDescription
                message = nil
            }
            isRefreshing = false
        }
    }

    func select(_ target: KitTarget) {
        selectedTargetID = target.id
        loadDetail(for: target)
    }

    func loadSelectedDetail() {
        guard let selectedTarget else {
            return
        }
        loadDetail(for: selectedTarget)
    }

    func loadDetail(for target: KitTarget) {
        guard !isLoadingDetail else {
            return
        }
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
                detail = try await RepoDetail(target: target, status: status, start: start, closeout: closeout)
            } catch {
                errorMessage = error.localizedDescription
            }
            isLoadingDetail = false
        }
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

    func checkForUpdates(silent: Bool = false) {
        guard !isCheckingForUpdates else {
            return
        }
        isCheckingForUpdates = true
        if !silent {
            message = "Checking for updates"
            errorMessage = nil
        }

        Task {
            let result = await updateChecker.check(currentVersion: Self.appVersion)
            updateCheckResult = result
            if result.updateAvailable {
                message = result.displayText
            } else if !silent {
                message = result.displayText
            }
            if let error = result.errorMessage, !silent {
                errorMessage = error
            }
            isCheckingForUpdates = false
        }
    }

    func openUpdate() {
        guard let result = updateCheckResult else {
            checkForUpdates()
            return
        }
        if let url = result.downloadURL ?? result.releaseURL {
            NSWorkspace.shared.open(url)
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

    private static var appVersion: String {
        Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "0.0.0"
    }
}
