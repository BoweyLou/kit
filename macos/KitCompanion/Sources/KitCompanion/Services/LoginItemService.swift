import Foundation
import ServiceManagement

enum LoginItemService {
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
        SMAppService.mainApp.status == .enabled
    }

    static func setEnabled(_ enabled: Bool) throws {
        if enabled {
            switch SMAppService.mainApp.status {
            case .enabled:
                return
            case .notRegistered:
                try SMAppService.mainApp.register()
            default:
                throw LoginItemError.unsupportedStatus(SMAppService.mainApp.status)
            }
        } else if SMAppService.mainApp.status == .enabled {
            try SMAppService.mainApp.unregister()
        }
    }
}
