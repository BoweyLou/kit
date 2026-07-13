import Foundation

enum LearningEventKind: String, Codable, CaseIterable, Identifiable {
    case observation, validation, feedback, incident
    var id: String { rawValue }
}

enum LearningEventOutcome: String, Codable, CaseIterable, Identifiable {
    case confirmed, inconclusive, regressed, unknown
    var id: String { rawValue }
}

enum LearningEventSource: String, Codable, CaseIterable, Identifiable {
    case human, agent, automation
    var id: String { rawValue }
}

enum LearningPrivacyLabel: String, Codable, CaseIterable, Identifiable {
    case publicOK = "public-ok"
    case `internal`
    case privateLocal = "private-local"
    case sensitiveLocal = "sensitive-local"
    var id: String { rawValue }
    var isExportable: Bool { self == .publicOK || self == .internal }
}

enum LearningProposalClassification: String, Codable, CaseIterable, Identifiable {
    case documentation, workflow, policy, harness, process, other
    var id: String { rawValue }
}

enum LearningDecisionOutcome: String, Codable, CaseIterable, Identifiable {
    case approved, rejected, deferred
    var id: String { rawValue }
}

enum LearningCommandRoute: String, Codable, CaseIterable {
    case status = "learn status"
    case eventList = "learn event list"
    case eventRecord = "learn event record"
    case proposalList = "learn proposal list"
    case proposalCreate = "learn proposal create"
    case decisionList = "learn decision list"
    case decisionRecord = "learn decision record"
    case contextList = "learn context list"
    case contextBuild = "learn context build"
    case threadSummaryList = "learn thread-summary list"
    case threadSummaryImport = "learn thread-summary import"
    case upstreamList = "learn upstream list"
    case upstreamReconcile = "learn upstream reconcile"
    case upstreamExport = "learn upstream export"
    case evaluate = "learn evaluate"

    var arguments: [String] { rawValue.split(separator: " ").map(String.init) }

    var writesSidecar: Bool {
        switch self {
        case .eventRecord, .proposalCreate, .decisionRecord, .contextBuild, .threadSummaryImport, .upstreamExport:
            return true
        default:
            return false
        }
    }
}

struct LearningCommand: Equatable {
    let route: LearningCommandRoute
    let arguments: [String]
    var writesSidecar: Bool { route.writesSidecar }
}

enum LearningCommandError: LocalizedError, Equatable {
    case rejected(String)

    var errorDescription: String? {
        switch self {
        case .rejected(let reason): return "Learning command rejected: \(reason)"
        }
    }
}

enum LearningCommandBuilder {
    static func status(repo: String) throws -> LearningCommand {
        try build(.status, repo: repo)
    }

    static func eventList(repo: String, limit: Int = 50) throws -> LearningCommand {
        try build(.eventList, repo: repo, values: [("--limit", String(limit))])
    }

    static func eventRecord(
        repo: String,
        kind: LearningEventKind,
        summary: String,
        evidence: [String],
        outcome: LearningEventOutcome,
        source: LearningEventSource,
        privacyLabel: LearningPrivacyLabel,
        approved: Bool
    ) throws -> LearningCommand {
        guard approved else { throw LearningCommandError.rejected("event recording requires explicit approval") }
        var values = [("--kind", kind.rawValue), ("--summary", summary)]
        values += evidence.map { ("--evidence", $0) }
        values += [
            ("--outcome", outcome.rawValue),
            ("--source", source.rawValue),
            ("--privacy-label", privacyLabel.rawValue),
            ("--approval-state", "approved")
        ]
        return try build(.eventRecord, repo: repo, values: values, switches: ["--approved"], switchBeforeLastValue: true)
    }

    static func proposalList(repo: String, limit: Int = 50) throws -> LearningCommand {
        try build(.proposalList, repo: repo, values: [("--limit", String(limit))])
    }

    static func proposalCreate(
        repo: String,
        title: String,
        classification: LearningProposalClassification,
        scopes: [String],
        recommendedChange: String,
        evidenceEventIDs: [String],
        privacyLabel: LearningPrivacyLabel
    ) throws -> LearningCommand {
        guard !title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
              !recommendedChange.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            throw LearningCommandError.rejected("proposal title and recommended change must not be blank")
        }
        var values = [("--title", title), ("--classification", classification.rawValue)]
        values += scopes.map { ("--scope", $0) }
        values.append(("--recommended-change", recommendedChange))
        values += evidenceEventIDs.map { ("--evidence-event", $0) }
        values.append(("--privacy-label", privacyLabel.rawValue))
        return try build(.proposalCreate, repo: repo, values: values)
    }

    static func decisionList(repo: String, limit: Int = 50) throws -> LearningCommand {
        try build(.decisionList, repo: repo, values: [("--limit", String(limit))])
    }

    static func decisionRecord(
        repo: String,
        proposalID: String,
        outcome: LearningDecisionOutcome,
        decider: String,
        rationale: String,
        followUp: [String],
        humanReviewConfirmed: Bool
    ) throws -> LearningCommand {
        guard !decider.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
              !rationale.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            throw LearningCommandError.rejected("decision decider and rationale must not be blank")
        }
        guard humanReviewConfirmed else { throw LearningCommandError.rejected("decision recording requires confirmed human review") }
        var values = [
            ("--proposal-id", proposalID),
            ("--outcome", outcome.rawValue),
            ("--decider", decider),
            ("--rationale", rationale)
        ]
        values += followUp.map { ("--follow-up", $0) }
        return try build(.decisionRecord, repo: repo, values: values, switches: ["--human-review-confirmed"])
    }

    static func contextList(repo: String, limit: Int = 50) throws -> LearningCommand {
        try build(.contextList, repo: repo, values: [("--limit", String(limit))])
    }

    static func contextBuild(repo: String, decisionID: String) throws -> LearningCommand {
        try build(.contextBuild, repo: repo, values: [("--decision-id", decisionID)])
    }

    static func threadSummaryList(repo: String, limit: Int = 50) throws -> LearningCommand {
        try build(.threadSummaryList, repo: repo, values: [("--limit", String(limit))])
    }

    static func threadSummaryImport(repo: String, inputPath: String, approved: Bool) throws -> LearningCommand {
        guard approved else { throw LearningCommandError.rejected("thread-summary import requires explicit approval") }
        return try build(.threadSummaryImport, repo: repo, values: [("--input", inputPath)], switches: ["--approved"])
    }

    static func upstreamList(repo: String, limit: Int = 50) throws -> LearningCommand {
        try build(.upstreamList, repo: repo, values: [("--limit", String(limit))])
    }

    static func upstreamReconcile(repo: String, limit: Int = 50) throws -> LearningCommand {
        try build(.upstreamReconcile, repo: repo, values: [("--limit", String(limit))])
    }

    static func upstreamExport(
        repo: String,
        decisionID: String,
        privacyLabel: LearningPrivacyLabel,
        redactionConfirmed: Bool
    ) throws -> LearningCommand {
        guard privacyLabel.isExportable else { throw LearningCommandError.rejected("upstream privacy must be public-ok or internal") }
        guard redactionConfirmed else { throw LearningCommandError.rejected("upstream export requires redaction confirmation") }
        return try build(
            .upstreamExport,
            repo: repo,
            values: [("--decision-id", decisionID), ("--privacy-label", privacyLabel.rawValue)],
            switches: ["--redaction-confirmed"]
        )
    }

    static func evaluate(repo: String) throws -> LearningCommand {
        try build(.evaluate, repo: repo)
    }

    private static func build(
        _ route: LearningCommandRoute,
        repo: String,
        values: [(String, String)] = [],
        switches: [String] = [],
        switchBeforeLastValue: Bool = false
    ) throws -> LearningCommand {
        var arguments = route.arguments + ["--repo=\(repo)"]
        if switchBeforeLastValue, let last = values.last {
            for (flag, value) in values.dropLast() { arguments.append("\(flag)=\(value)") }
            arguments += switches
            arguments.append("\(last.0)=\(last.1)")
        } else {
            for (flag, value) in values { arguments.append("\(flag)=\(value)") }
            arguments += switches
        }
        arguments.append("--json")
        return try LearningCommandValidator.validate(arguments, selectedRepo: repo)
    }
}

enum LearningCommandValidator {
    private struct Rule {
        let valueFlags: Set<String>
        let switchFlags: Set<String>
        let required: Set<String>
        let repeatable: Set<String>
    }

    private static let banned = Set(["--apply", "--global", "--write", "--write-sidecar", "--force"])

    static func validate(_ arguments: [String], selectedRepo: String) throws -> LearningCommand {
        guard let first = arguments.first, first == "learn" else {
            throw LearningCommandError.rejected("only the exact learn namespace is accepted")
        }
        guard isAbsolute(selectedRepo) else { throw LearningCommandError.rejected("selected repository must be absolute") }
        guard let route = route(for: arguments) else { throw LearningCommandError.rejected("unknown or namespace-only route") }
        let prefix = route.arguments
        let tail = Array(arguments.dropFirst(prefix.count))
        guard !tail.contains(where: banned.contains) else { throw LearningCommandError.rejected("forbidden mutation flag") }

        let rule = rule(for: route)
        var values: [String: [String]] = [:]
        var switches = Set<String>()
        var index = 0
        while index < tail.count {
            let token = tail[index]
            if let separator = token.firstIndex(of: "=") {
                let flag = String(token[..<separator])
                let value = String(token[token.index(after: separator)...])
                guard flag.hasPrefix("--"), rule.valueFlags.contains(flag), !value.isEmpty else {
                    throw LearningCommandError.rejected("unknown flag or missing inline value \(flag)")
                }
                if values[flag] != nil, !rule.repeatable.contains(flag) {
                    throw LearningCommandError.rejected("duplicate singleton flag \(flag)")
                }
                values[flag, default: []].append(value)
                index += 1
                continue
            }

            let flag = token
            guard flag.hasPrefix("--") else { throw LearningCommandError.rejected("unexpected positional argument") }
            if rule.switchFlags.contains(flag) {
                guard !switches.contains(flag) else { throw LearningCommandError.rejected("duplicate singleton flag \(flag)") }
                switches.insert(flag)
                index += 1
                continue
            }
            guard rule.valueFlags.contains(flag), index + 1 < tail.count else {
                throw LearningCommandError.rejected("unknown flag or missing value \(flag)")
            }
            let value = tail[index + 1]
            guard !value.hasPrefix("-"), !value.isEmpty else { throw LearningCommandError.rejected("ambiguous value for \(flag); use --flag=value") }
            if values[flag] != nil, !rule.repeatable.contains(flag) {
                throw LearningCommandError.rejected("duplicate singleton flag \(flag)")
            }
            values[flag, default: []].append(value)
            index += 2
        }

        let present = Set(values.keys).union(switches)
        guard rule.required.isSubset(of: present) else {
            throw LearningCommandError.rejected("required flags are missing")
        }
        guard values["--repo"]?.count == 1, switches.contains("--json") else {
            throw LearningCommandError.rejected("exactly one --repo and --json are required")
        }
        let repo = values["--repo"]![0]
        guard isAbsolute(repo), standardized(repo) == standardized(selectedRepo) else {
            throw LearningCommandError.rejected("command repository does not match the selected repository")
        }
        try validateValues(route: route, values: values, switches: switches)
        return LearningCommand(route: route, arguments: arguments)
    }

    private static func route(for arguments: [String]) -> LearningCommandRoute? {
        LearningCommandRoute.allCases
            .sorted { $0.arguments.count > $1.arguments.count }
            .first { route in arguments.count > route.arguments.count && Array(arguments.prefix(route.arguments.count)) == route.arguments }
    }

    private static func rule(for route: LearningCommandRoute) -> Rule {
        var valueFlags = Set(["--repo"])
        var switchFlags = Set(["--json"])
        var required = Set(["--repo", "--json"])
        var repeatable = Set<String>()

        switch route {
        case .status, .evaluate:
            break
        case .eventList, .proposalList, .decisionList, .contextList, .threadSummaryList, .upstreamList, .upstreamReconcile:
            valueFlags.insert("--limit"); required.insert("--limit")
        case .eventRecord:
            valueFlags.formUnion(["--kind", "--summary", "--evidence", "--outcome", "--source", "--privacy-label", "--approval-state"])
            switchFlags.insert("--approved")
            required.formUnion(["--kind", "--summary", "--outcome", "--source", "--privacy-label", "--approval-state", "--approved"])
            repeatable.insert("--evidence")
        case .proposalCreate:
            valueFlags.formUnion(["--title", "--classification", "--scope", "--recommended-change", "--evidence-event", "--privacy-label"])
            required.formUnion(["--title", "--classification", "--scope", "--recommended-change", "--evidence-event", "--privacy-label"])
            repeatable.formUnion(["--scope", "--evidence-event"])
        case .decisionRecord:
            valueFlags.formUnion(["--proposal-id", "--outcome", "--decider", "--rationale", "--follow-up"])
            switchFlags.insert("--human-review-confirmed")
            required.formUnion(["--proposal-id", "--outcome", "--decider", "--rationale", "--human-review-confirmed"])
            repeatable.insert("--follow-up")
        case .contextBuild:
            valueFlags.insert("--decision-id"); required.insert("--decision-id")
        case .threadSummaryImport:
            valueFlags.insert("--input"); switchFlags.insert("--approved")
            required.formUnion(["--input", "--approved"])
        case .upstreamExport:
            valueFlags.formUnion(["--decision-id", "--privacy-label"]); switchFlags.insert("--redaction-confirmed")
            required.formUnion(["--decision-id", "--privacy-label", "--redaction-confirmed"])
        }
        return Rule(valueFlags: valueFlags, switchFlags: switchFlags, required: required, repeatable: repeatable)
    }

    private static func validateValues(route: LearningCommandRoute, values: [String: [String]], switches: Set<String>) throws {
        func one(_ flag: String) -> String { values[flag]?.first ?? "" }
        func bounded(_ flag: String, max: Int, required: Bool = true) throws {
            let entries = values[flag] ?? []
            if entries.count > max || (required && entries.isEmpty) || entries.contains(where: { $0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }) {
                throw LearningCommandError.rejected("invalid bounded values for \(flag)")
            }
        }
        if let limitText = values["--limit"]?.first {
            guard let limit = Int(limitText), (1...50).contains(limit) else { throw LearningCommandError.rejected("list limit must be 1...50") }
        }
        switch route {
        case .eventRecord:
            guard LearningEventKind(rawValue: one("--kind")) != nil,
                  LearningEventOutcome(rawValue: one("--outcome")) != nil,
                  LearningEventSource(rawValue: one("--source")) != nil,
                  LearningPrivacyLabel(rawValue: one("--privacy-label")) != nil,
                  one("--approval-state") == "approved", switches.contains("--approved") else {
                throw LearningCommandError.rejected("invalid event enum or approval value")
            }
            try bounded("--summary", max: 1); guard one("--summary").count <= 500 else { throw LearningCommandError.rejected("summary exceeds 500 characters") }
            try bounded("--evidence", max: 10, required: false)
            guard (values["--evidence"] ?? []).allSatisfy({ $0.count <= 500 }) else { throw LearningCommandError.rejected("evidence exceeds 500 characters") }
        case .proposalCreate:
            guard LearningProposalClassification(rawValue: one("--classification")) != nil,
                  LearningPrivacyLabel(rawValue: one("--privacy-label")) != nil else { throw LearningCommandError.rejected("invalid proposal enum") }
            guard !one("--title").trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
                  !one("--recommended-change").trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
                  one("--title").count <= 160, one("--recommended-change").count <= 500 else { throw LearningCommandError.rejected("proposal text is blank or exceeds bounds") }
            try bounded("--scope", max: 10); try bounded("--evidence-event", max: 10)
            guard (values["--scope"] ?? []).allSatisfy({ $0.count <= 200 }),
                  Set(values["--evidence-event"] ?? []).count == (values["--evidence-event"] ?? []).count,
                  (values["--evidence-event"] ?? []).allSatisfy({ matches($0, prefix: "evt-") }) else {
                throw LearningCommandError.rejected("invalid proposal scope or event lineage")
            }
        case .decisionRecord:
            guard matches(one("--proposal-id"), prefix: "prop-"),
                  LearningDecisionOutcome(rawValue: one("--outcome")) != nil,
                  !one("--decider").trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
                  !one("--rationale").trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
                  one("--decider").count <= 120,
                  one("--rationale").count <= 500 else { throw LearningCommandError.rejected("invalid decision values") }
            try bounded("--follow-up", max: 10, required: false)
            guard (values["--follow-up"] ?? []).allSatisfy({ $0.count <= 500 }) else { throw LearningCommandError.rejected("follow-up exceeds bounds") }
        case .contextBuild:
            guard matches(one("--decision-id"), prefix: "dec-") else { throw LearningCommandError.rejected("invalid decision identifier") }
        case .threadSummaryImport:
            guard isAbsolute(one("--input")) else { throw LearningCommandError.rejected("thread-summary input must be absolute") }
        case .upstreamExport:
            guard matches(one("--decision-id"), prefix: "dec-"),
                  let privacy = LearningPrivacyLabel(rawValue: one("--privacy-label")), privacy.isExportable else {
                throw LearningCommandError.rejected("invalid export decision or privacy")
            }
        default:
            break
        }
    }

    private static func isAbsolute(_ path: String) -> Bool { URL(fileURLWithPath: path).path.hasPrefix("/") && path.hasPrefix("/") }
    private static func standardized(_ path: String) -> String { URL(fileURLWithPath: path).standardizedFileURL.path }
    private static func matches(_ value: String, prefix: String) -> Bool {
        guard value.hasPrefix(prefix), value.count == prefix.count + 20 else { return false }
        return value.dropFirst(prefix.count).allSatisfy { $0.isHexDigit && !$0.isUppercase }
    }
}
