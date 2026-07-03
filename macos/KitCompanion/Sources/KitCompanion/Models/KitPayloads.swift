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
    struct HumanSummary: Codable {
        struct Remaining: Codable, Identifiable {
            let id = UUID()
            let code: String?
            let title: String?
            let category: String?
            let count: Int?

            enum CodingKeys: String, CodingKey {
                case code
                case title
                case category
                case count
            }
        }

        let title: String?
        let status: String?
        let plainReason: String?
        let whyItBlocks: String?
        let recommendedAction: String?
        let safeNextCommand: String?
        let completed: [String]?
        let remaining: [Remaining]?

        enum CodingKeys: String, CodingKey {
            case title
            case status
            case plainReason = "plain_reason"
            case whyItBlocks = "why_it_blocks"
            case recommendedAction = "recommended_action"
            case safeNextCommand = "safe_next_command"
            case completed
            case remaining
        }
    }

    struct NextAction: Codable {
        let command: String?
        let mutating: Bool?
        let reason: String?
    }

    struct Blocker: Codable, Identifiable {
        let id = UUID()
        let code: String?
        let message: String?
        let title: String?
        let category: String?
        let plainReason: String?
        let whyItBlocks: String?
        let recommendedAction: String?
        let safeNextCommand: String?
        let automationLevel: String?
        let count: Int?

        enum CodingKeys: String, CodingKey {
            case code
            case message
            case title
            case category
            case plainReason = "plain_reason"
            case whyItBlocks = "why_it_blocks"
            case recommendedAction = "recommended_action"
            case safeNextCommand = "safe_next_command"
            case automationLevel = "automation_level"
            case count
        }
    }

    let canClaimDone: Bool?
    let completionState: String?
    let nextAction: NextAction?
    let claimBlockers: [Blocker]?
    let blockerExplanations: [Blocker]?
    let humanSummary: HumanSummary?

    enum CodingKeys: String, CodingKey {
        case canClaimDone = "can_claim_done"
        case completionState = "completion_state"
        case nextAction = "next_action"
        case claimBlockers = "claim_blockers"
        case blockerExplanations = "blocker_explanations"
        case humanSummary = "human_summary"
    }
}

struct CloseoutFixEvent: Codable, Identifiable {
    var id = UUID()
    let event: String
    let jobId: String?
    let createdAt: String?
    let text: String?
    let result: String?
    let receipt: String?
    let exitCode: Int?
    let count: Int?
    let branch: String?

    enum CodingKeys: String, CodingKey {
        case event
        case jobId = "job_id"
        case createdAt = "created_at"
        case text
        case result
        case receipt
        case exitCode = "exit_code"
        case count
        case branch
    }

    var displayText: String {
        switch event {
        case "job-started":
            return "Job started"
        case "runner-started":
            return "Runner started"
        case "agent-output":
            return text ?? "Agent event"
        case "agent-stderr":
            return text ?? "Agent stderr"
        case "worktrees-pruned":
            return "\(count ?? 0) worktrees pruned"
        case "branch-pushed":
            return "Pushed \(branch ?? "branch")"
        case "job-finished":
            return "Job \(result ?? "finished")"
        case "job-completed":
            return "Job \(result ?? "completed")"
        default:
            return event
        }
    }
}

struct CloseoutFixPayload: Codable {
    let command: String?
    let mode: String?
    let jobId: String?
    let jobDir: String?
    let resultPath: String?
    let repo: String?
    let result: String?
    let commits: [CloseoutFixCommit]?
    let branchesPushed: [CloseoutFixBranchPush]?
    let worktreesPruned: [CloseoutFixWorktree]?
    let receipts: [CloseoutFixReceipt]?
    let blockers: [String]?
    let blockerExplanations: [CloseoutPayload.Blocker]?
    let humanSummary: CloseoutPayload.HumanSummary?
    let exitCode: Int?
    let noPush: Bool?

    enum CodingKeys: String, CodingKey {
        case command
        case mode
        case jobId = "job_id"
        case jobDir = "job_dir"
        case resultPath = "result_path"
        case repo
        case result
        case commits
        case branchesPushed = "branches_pushed"
        case worktreesPruned = "worktrees_pruned"
        case receipts
        case blockers
        case blockerExplanations = "blocker_explanations"
        case humanSummary = "human_summary"
        case exitCode = "exit_code"
        case noPush = "no_push"
    }
}

struct CloseoutFixCommit: Codable, Identifiable {
    var id: String { sha ?? shortSha ?? subject ?? UUID().uuidString }

    let sha: String?
    let shortSha: String?
    let subject: String?
    let files: [String]?

    enum CodingKeys: String, CodingKey {
        case sha
        case shortSha = "short_sha"
        case subject
        case files
    }
}

struct CloseoutFixBranchPush: Codable, Identifiable {
    var id: String { branch ?? command ?? UUID().uuidString }

    let branch: String?
    let command: String?
    let exitCode: Int?
    let stderr: String?

    enum CodingKeys: String, CodingKey {
        case branch
        case command
        case exitCode = "exit_code"
        case stderr
    }
}

struct CloseoutFixWorktree: Codable, Identifiable {
    var id: String { path ?? branch ?? UUID().uuidString }

    let path: String?
    let branch: String?
}

struct CloseoutFixReceipt: Codable, Identifiable {
    var id: String { path ?? kind ?? UUID().uuidString }

    let path: String?
    let kind: String?
}

struct CloseoutFixFinalPayloadLine: Codable {
    let event: String
    let payload: CloseoutFixPayload?
}

struct CloseoutFixJob: Identifiable {
    let id: String
    let targetName: String
    let targetRoot: String
    let startedAt: Date
    var isRunning: Bool
    var events: [CloseoutFixEvent]
    var payload: CloseoutFixPayload?
    var errorMessage: String?

    var statusText: String {
        if isRunning {
            return "running"
        }
        if let result = payload?.result {
            return result
        }
        if errorMessage != nil {
            return "failed"
        }
        return "queued"
    }
}

struct KitWriteAction: Identifiable, Equatable {
    let id: String
    let title: String
    let confirmation: String
    let arguments: [String]
    let workingDirectory: String?
    let successMessage: String
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
