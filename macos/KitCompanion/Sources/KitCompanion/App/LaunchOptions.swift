import Foundation

enum DashboardSection: String, CaseIterable, Identifiable, Codable {
    case overview
    case commands
    case workflows
    case batch
    case learning

    var id: String { rawValue }

    var label: String {
        switch self {
        case .overview: return "Overview"
        case .commands: return "Commands"
        case .workflows: return "Workflows"
        case .batch: return "Batch"
        case .learning: return "Learning"
        }
    }
}

struct KitCompanionLaunchOptions: Equatable {
    let dashboardSection: DashboardSection

    static func parse(arguments: [String]) -> KitCompanionLaunchOptions? {
        guard arguments.count == 3,
              arguments[1] == "--open-dashboard",
              let section = DashboardSection(rawValue: arguments[2]) else {
            return nil
        }
        return KitCompanionLaunchOptions(dashboardSection: section)
    }
}
