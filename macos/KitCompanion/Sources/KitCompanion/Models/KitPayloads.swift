import Foundation

struct KitCommandResult {
    let stdout: String
    let stderr: String
    let exitCode: Int32

    var succeeded: Bool {
        exitCode == 0
    }
}

struct KitTarget: Codable, Identifiable, Hashable {
    let id: String
    let name: String
    let root: String
    let status: String
    let dirtyCount: Int
    let dirtyFiles: [String]
    let kitVersion: String?
    let installVersion: String?
    let lastSeenAt: String?

    enum CodingKeys: String, CodingKey {
        case id
        case name
        case root
        case status
        case dirtyCount = "dirty_count"
        case dirtyFiles = "dirty_files"
        case kitVersion = "kit_version"
        case installVersion = "install_version"
        case lastSeenAt = "last_seen_at"
    }

    var isDirty: Bool {
        status == "dirty" || dirtyCount > 0
    }

    var displayStatus: String {
        if isDirty {
            return "\(dirtyCount) changed"
        }
        return status.capitalized
    }
}

struct TargetStatusCounts: Codable, Equatable {
    let dirty: Int?
    let ready: Int?
}

struct TargetReportSummary: Codable, Equatable {
    let total: Int?
    let clean: Int?
    let dirty: Int?
    let statuses: TargetStatusCounts?
}

struct TargetReportPayload: Codable {
    let command: String
    let exitCode: Int?
    let summary: TargetReportSummary?
    let targets: [KitTarget]

    enum CodingKeys: String, CodingKey {
        case command
        case exitCode = "exit_code"
        case summary
        case targets
    }
}

struct KitDrift: Codable {
    let classification: String?
    let reason: String?
    let severity: String?

    var hasWarning: Bool {
        guard let classification else {
            return false
        }
        return classification != "current" && classification != "not-installed"
    }
}

struct GitWorktreeState: Codable {
    let dirty: Bool?
    let count: Int?
    let state: String?
    let changedFiles: [String]?

    enum CodingKeys: String, CodingKey {
        case dirty
        case count
        case state
        case changedFiles = "changed_files"
    }
}

struct StatusPayload: Codable {
    let command: String
    let gitWorktreeState: GitWorktreeState?
    let kitDrift: KitDrift?

    enum CodingKeys: String, CodingKey {
        case command
        case gitWorktreeState = "git_worktree_state"
        case kitDrift = "kit_drift"
    }
}

struct StartPayload: Codable {
    struct Journey: Codable {
        let label: String?
        let reason: String?
    }

    struct Mode: Codable {
        let selected: String?
        let confidence: String?
    }

    struct NextStep: Codable, Identifiable {
        let id = UUID()
        let label: String?
        let command: String?
        let mutating: Bool?
        let reason: String?

        enum CodingKeys: String, CodingKey {
            case label
            case command
            case mutating
            case reason
        }
    }

    let command: String
    let journey: Journey?
    let mode: Mode?
    let nextSteps: [NextStep]?

    enum CodingKeys: String, CodingKey {
        case command
        case journey
        case mode
        case nextSteps = "next_steps"
    }
}

struct CloseoutPayload: Codable {
    struct NextAction: Codable {
        let command: String?
        let mutating: Bool?
        let reason: String?
    }

    struct Blocker: Codable, Identifiable {
        let id = UUID()
        let code: String?
        let message: String?

        enum CodingKeys: String, CodingKey {
            case code
            case message
        }
    }

    let canClaimDone: Bool?
    let completionState: String?
    let nextAction: NextAction?
    let claimBlockers: [Blocker]?

    enum CodingKeys: String, CodingKey {
        case canClaimDone = "can_claim_done"
        case completionState = "completion_state"
        case nextAction = "next_action"
        case claimBlockers = "claim_blockers"
    }
}

struct UpdatePreviewPayload: Codable {
    let command: String?
    let mode: String?
    let exitCode: Int?
    let summary: TargetReportSummary?
    let targets: [KitUpdateTarget]?

    enum CodingKeys: String, CodingKey {
        case command
        case mode
        case exitCode = "exit_code"
        case summary
        case targets
    }
}

struct KitUpdateTarget: Codable, Identifiable {
    var id: String {
        repo ?? name ?? UUID().uuidString
    }

    let name: String?
    let repo: String?
    let status: String?
    let exitCode: Int?

    enum CodingKeys: String, CodingKey {
        case name
        case repo
        case status
        case exitCode = "exit_code"
    }
}

struct RepoDetail {
    var target: KitTarget
    var status: StatusPayload?
    var start: StartPayload?
    var closeout: CloseoutPayload?
}

struct UpdateCheckResult {
    let currentVersion: String
    let latestVersion: String?
    let releaseURL: URL?
    let downloadURL: URL?
    let checkedAt: Date
    let errorMessage: String?

    var updateAvailable: Bool {
        guard let latestVersion else {
            return false
        }
        return VersionComparator.isVersion(latestVersion, newerThan: currentVersion)
    }

    var displayText: String {
        if let errorMessage {
            return errorMessage
        }
        guard let latestVersion else {
            return "No release information found"
        }
        if updateAvailable {
            return "Kit Companion \(latestVersion) is available"
        }
        return "Kit Companion is current"
    }
}

enum VersionComparator {
    static func isVersion(_ candidate: String, newerThan current: String) -> Bool {
        normalizedParts(candidate).lexicographicallyPrecedes(normalizedParts(current)) == false
            && normalizedParts(candidate) != normalizedParts(current)
    }

    private static func normalizedParts(_ value: String) -> [Int] {
        value
            .trimmingCharacters(in: CharacterSet(charactersIn: "vV"))
            .split(separator: ".")
            .map { part in
                let digits = part.prefix { $0.isNumber }
                return Int(digits) ?? 0
            }
            .padding(to: 3, with: 0)
    }
}

private extension Array where Element == Int {
    func padding(to count: Int, with value: Int) -> [Int] {
        if self.count >= count {
            return self
        }
        return self + Array(repeating: value, count: count - self.count)
    }
}
