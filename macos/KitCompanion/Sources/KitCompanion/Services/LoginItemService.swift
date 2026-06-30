import Foundation
import ServiceManagement

enum LoginItemService {
    struct State: Equatable {
        let statusRawValue: Int
        let isEnabled: Bool
        let label: String
        let message: String
        let needsApproval: Bool
        let isInstalledInApplications: Bool
        let bundlePath: String
    }

    enum LoginItemError: LocalizedError {
        case unsupportedStatus(SMAppService.Status)

        var errorDescription: String? {
            switch self {
            case .unsupportedStatus(let status):
                return "Launch at Login is not available in the current state: \(status.rawValue)"
            }
        }
    }

    static var isEnabled: Bool {
        currentState().isEnabled
    }

    static func currentState() -> State {
        let status = SMAppService.mainApp.status
        return State(
            statusRawValue: status.rawValue,
            isEnabled: status == .enabled,
            label: label(for: status),
            message: message(for: status),
            needsApproval: status == .requiresApproval,
            isInstalledInApplications: isInstalledInApplications,
            bundlePath: Bundle.main.bundlePath
        )
    }

    @discardableResult
    static func setEnabled(_ enabled: Bool) throws -> State {
        if enabled {
            switch SMAppService.mainApp.status {
            case .enabled:
                break
            case .notRegistered:
                try SMAppService.mainApp.register()
            case .requiresApproval:
                break
            default:
                throw LoginItemError.unsupportedStatus(SMAppService.mainApp.status)
            }
        } else {
            switch SMAppService.mainApp.status {
            case .enabled, .requiresApproval:
                try SMAppService.mainApp.unregister()
            case .notRegistered:
                break
            default:
                throw LoginItemError.unsupportedStatus(SMAppService.mainApp.status)
            }
        }
        return currentState()
    }

    static func label(for status: SMAppService.Status) -> String {
        switch status {
        case .enabled:
            return "Enabled"
        case .notRegistered:
            return "Off"
        case .requiresApproval:
            return "Needs Approval"
        case .notFound:
            return "Unavailable"
        @unknown default:
            return "Unknown"
        }
    }

    static func message(for status: SMAppService.Status) -> String {
        switch status {
        case .enabled:
            return "Kit Companion will open automatically when you log in."
        case .notRegistered:
            return "Kit Companion is not registered to open at login."
        case .requiresApproval:
            return "macOS needs approval in System Settings before Kit Companion can open at login."
        case .notFound:
            return "macOS could not find the app bundle for login item registration."
        @unknown default:
            return "macOS returned an unknown login item state."
        }
    }

    static func openSystemSettings() {
        SMAppService.openSystemSettingsLoginItems()
    }

    private static var isInstalledInApplications: Bool {
        let path = URL(fileURLWithPath: Bundle.main.bundlePath).standardizedFileURL.path
        let homeApplications = (NSHomeDirectory() as NSString).appendingPathComponent("Applications")
        return path.hasPrefix("/Applications/") || path.hasPrefix(homeApplications + "/")
    }
}
