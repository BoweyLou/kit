import Foundation
import Darwin
import CryptoKit

struct LearningWriteMetadata: Codable, Equatable {
    let performed: Bool
    let paths: [String]
    let reason: String

    static let none = LearningWriteMetadata(performed: false, paths: [], reason: "no writes")
}

struct LearningSidecarRepoIdentity: Codable, Equatable {
    let root: String
    let hash: String
    let id: String
}

struct LearningSidecarState: Codable, Equatable {
    let repoStateDir: String
    let repo: LearningSidecarRepoIdentity

    enum CodingKeys: String, CodingKey {
        case repoStateDir = "repo_state_dir"
        case repo
    }
}

protocol LearningActionMetadata {
    var action: String { get }
}

protocol LearningWriteSuccessMetadata {
    var policyState: String { get }
    var policy: LearningPolicyStatus { get }
    var gate: LearningGate { get }
}

protocol LearningPayloadMetadata {
    var schemaVersion: Int { get }
    var command: String { get }
    var repo: String { get }
    var targetRepoWrites: LearningWriteMetadata { get }
    var sidecarWrites: LearningWriteMetadata { get }
    var globalWrites: LearningWriteMetadata { get }
    var sidecarState: LearningSidecarState { get }
    var exitCode: Int { get }
}

struct LearningPolicyStatus: Codable, Equatable {
    let state: String
    let path: String?
    let ownership: String?
    let enabled: Bool?
    let policyID: String?
    let schemaVersion: Int?

    enum CodingKeys: String, CodingKey {
        case state, path, ownership, enabled
        case policyID = "policy_id"
        case schemaVersion = "schema_version"
    }
}

struct LearningPaths: Codable, Equatable {
    let policy: String?
    let schemas: [String: String]?
    let sidecar: [String: String]
}

struct LearningWriteGuarantees: Codable, Equatable {
    let targetRepoWrites: Bool
    let sidecarWrites: Bool
    let globalToolWrites: Bool
    let note: String

    enum CodingKeys: String, CodingKey {
        case targetRepoWrites = "target_repo_writes"
        case sidecarWrites = "sidecar_writes"
        case globalToolWrites = "global_tool_writes"
        case note
    }
}

struct LearningStatusPayload: Codable, LearningPayloadMetadata, Equatable {
    let schemaVersion: Int
    let command: String
    let repo: String
    let policyState: String
    let policy: LearningPolicyStatus
    let learningPaths: LearningPaths
    let safeNextCommands: [String]
    let writeGuarantees: LearningWriteGuarantees
    let targetRepoWrites: LearningWriteMetadata
    let sidecarWrites: LearningWriteMetadata
    let globalWrites: LearningWriteMetadata
    let sidecarState: LearningSidecarState
    let exitCode: Int

    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"
        case command, repo
        case policyState = "policy_state"
        case policy
        case learningPaths = "learning_paths"
        case safeNextCommands = "safe_next_commands"
        case writeGuarantees = "write_guarantees"
        case targetRepoWrites = "target_repo_writes"
        case sidecarWrites = "sidecar_writes"
        case globalWrites = "global_writes"
        case sidecarState = "sidecar_state"
        case exitCode = "exit_code"
    }

    func replacingMetadata(targetRepoWrites: LearningWriteMetadata) -> LearningStatusPayload {
        LearningStatusPayload(
            schemaVersion: schemaVersion,
            command: command,
            repo: repo,
            policyState: policyState,
            policy: policy,
            learningPaths: learningPaths,
            safeNextCommands: safeNextCommands,
            writeGuarantees: writeGuarantees,
            targetRepoWrites: targetRepoWrites,
            sidecarWrites: sidecarWrites,
            globalWrites: globalWrites,
            sidecarState: sidecarState,
            exitCode: exitCode
        )
    }
}

struct LearningProvenance: Codable, Equatable {
    let source: LearningEventSource
    let capture: String
}

struct LearningSupervision: Codable, Equatable {
    let humanApprovalRequired: Bool
    let approvalState: String
    let approvalFlag: Bool

    enum CodingKeys: String, CodingKey {
        case humanApprovalRequired = "human_approval_required"
        case approvalState = "approval_state"
        case approvalFlag = "approval_flag"
    }
}

struct LearningEvent: Codable, Equatable, Identifiable {
    let schemaVersion: Int
    let eventID: String
    let occurredAt: String
    let policyID: String
    let repo: String
    let kind: LearningEventKind
    let summary: String
    let evidence: [String]
    let outcome: LearningEventOutcome
    let provenance: LearningProvenance
    let privacyLabel: LearningPrivacyLabel
    let supervision: LearningSupervision

    var id: String { eventID }

    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"
        case eventID = "event_id"
        case occurredAt = "occurred_at"
        case policyID = "policy_id"
        case repo, kind, summary, evidence, outcome, provenance
        case privacyLabel = "privacy_label"
        case supervision
    }
}

struct LearningProposalLineage: Codable, Equatable {
    let evidenceEventIDs: [String]
    enum CodingKeys: String, CodingKey { case evidenceEventIDs = "evidence_event_ids" }
}

struct LearningNonExecutionGuarantee: Codable, Equatable {
    let enforced: Bool
    let recommendationExecutionPermitted: Bool
    let prohibitedWrites: [String]
    let note: String

    enum CodingKeys: String, CodingKey {
        case enforced, note
        case recommendationExecutionPermitted = "recommendation_execution_permitted"
        case prohibitedWrites = "prohibited_writes"
    }
}

struct LearningProposal: Codable, Equatable, Identifiable {
    let schemaVersion: Int
    let proposalID: String
    let createdAt: String
    let policyID: String
    let repo: String
    let title: String
    let classification: LearningProposalClassification
    let scope: [String]
    let recommendedChange: String
    let lineage: LearningProposalLineage
    let privacyLabel: LearningPrivacyLabel
    let status: String
    let humanApprovalRequired: Bool
    let decisionID: String?
    let nonExecutionGuarantee: LearningNonExecutionGuarantee

    var id: String { proposalID }

    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"
        case proposalID = "proposal_id"
        case createdAt = "created_at"
        case policyID = "policy_id"
        case repo, title, classification, scope
        case recommendedChange = "recommended_change"
        case lineage
        case privacyLabel = "privacy_label"
        case status
        case humanApprovalRequired = "human_approval_required"
        case decisionID = "decision_id"
        case nonExecutionGuarantee = "non_execution_guarantee"
    }
}

struct LearningDecisionLineage: Codable, Equatable {
    let proposalID: String
    let evidenceEventIDs: [String]
    enum CodingKeys: String, CodingKey {
        case proposalID = "proposal_id"
        case evidenceEventIDs = "evidence_event_ids"
    }
}

struct LearningHumanReview: Codable, Equatable {
    let required: Bool
    let confirmed: Bool
    let capture: String
}

struct LearningDecision: Codable, Equatable, Identifiable {
    let schemaVersion: Int
    let decisionID: String
    let decidedAt: String
    let policyID: String
    let repo: String
    let proposalID: String
    let outcome: LearningDecisionOutcome
    let rationale: String
    let decider: String
    let humanReview: LearningHumanReview
    let lineage: LearningDecisionLineage
    let privacyLabel: LearningPrivacyLabel
    let followUp: [String]
    let nonExecutionGuarantee: LearningNonExecutionGuarantee

    var id: String { decisionID }

    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"
        case decisionID = "decision_id"
        case decidedAt = "decided_at"
        case policyID = "policy_id"
        case repo
        case proposalID = "proposal_id"
        case outcome, rationale, decider
        case humanReview = "human_review"
        case lineage
        case privacyLabel = "privacy_label"
        case followUp = "follow_up"
        case nonExecutionGuarantee = "non_execution_guarantee"
    }
}

struct LearningDecisionProposalLineage: Codable, Equatable {
    let decisionID: String
    let proposalID: String
    enum CodingKeys: String, CodingKey {
        case decisionID = "decision_id"
        case proposalID = "proposal_id"
    }
}

struct LearningGuidance: Codable, Equatable {
    let classification: LearningProposalClassification
    let scope: [String]
    let recommendedChange: String
    enum CodingKeys: String, CodingKey {
        case classification, scope
        case recommendedChange = "recommended_change"
    }
}

struct LearningRetention: Codable, Equatable {
    let days: Int
    let expiresAt: String
    enum CodingKeys: String, CodingKey { case days; case expiresAt = "expires_at" }
}

struct LearningContext: Codable, Equatable, Identifiable {
    let schemaVersion: Int
    let contextID: String
    let capturedAt: String
    let policyID: String
    let repo: String
    let lineage: LearningDecisionProposalLineage
    let guidance: LearningGuidance
    let privacyLabel: LearningPrivacyLabel
    let retention: LearningRetention
    let sidecarOnlyGuidance: Bool
    let nonExecutionGuarantee: LearningNonExecutionGuarantee

    var id: String { contextID }

    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"
        case contextID = "context_id"
        case capturedAt = "captured_at"
        case policyID = "policy_id"
        case repo, lineage, guidance
        case privacyLabel = "privacy_label"
        case retention
        case sidecarOnlyGuidance = "sidecar_only_guidance"
        case nonExecutionGuarantee = "non_execution_guarantee"
    }
}

struct LearningUpstreamOrigin: Codable, Equatable {
    let kind: String
    let repositoryID: String
    enum CodingKeys: String, CodingKey { case kind; case repositoryID = "repository_id" }
}

struct LearningSourceBaseline: Codable, Equatable {
    let sourceRef: String
    let version: String
    enum CodingKeys: String, CodingKey { case sourceRef = "source_ref"; case version }
}

struct LearningUpstreamCandidate: Codable, Equatable, Identifiable {
    let schemaVersion: Int
    let candidateID: String
    let createdAt: String
    let policyID: String
    let lineage: LearningDecisionProposalLineage
    let recommendation: LearningGuidance
    let origin: LearningUpstreamOrigin
    let sourceBaseline: LearningSourceBaseline
    let privacyLabel: LearningPrivacyLabel
    let redactionConfirmed: Bool

    var id: String { candidateID }

    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"
        case candidateID = "candidate_id"
        case createdAt = "created_at"
        case policyID = "policy_id"
        case lineage, recommendation, origin
        case sourceBaseline = "source_baseline"
        case privacyLabel = "privacy_label"
        case redactionConfirmed = "redaction_confirmed"
    }
}

struct LearningReconcileCandidate: Codable, Equatable, Identifiable {
    let candidateID: String
    let baseline: LearningSourceBaseline
    let currentSource: LearningSourceBaseline?
    let status: String
    let revalidationRequired: Bool
    var id: String { candidateID }

    enum CodingKeys: String, CodingKey {
        case candidateID = "candidate_id"
        case baseline
        case currentSource = "current_source"
        case status
        case revalidationRequired = "revalidation_required"
    }
}

struct LearningRolloutGuidance: Codable, Equatable {
    let sourceReviewRequired: Bool
    let automaticPropagation: Bool
    let normalSourceWorkflow: [String]
    let note: String

    enum CodingKeys: String, CodingKey {
        case sourceReviewRequired = "source_review_required"
        case automaticPropagation = "automatic_propagation"
        case normalSourceWorkflow = "normal_source_workflow"
        case note
    }
}

struct LearningEventListPayload: Codable, LearningPayloadMetadata, LearningActionMetadata, Equatable {
    let schemaVersion: Int; let command: String; let action: String; let repo: String
    let eventsPath: String; let events: [LearningEvent]; let count: Int; let warnings: [String]
    let targetRepoWrites: LearningWriteMetadata; let sidecarWrites: LearningWriteMetadata; let globalWrites: LearningWriteMetadata
    let sidecarState: LearningSidecarState; let exitCode: Int
    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"; case command, action, repo
        case eventsPath = "events_path"; case events, count, warnings
        case targetRepoWrites = "target_repo_writes"; case sidecarWrites = "sidecar_writes"; case globalWrites = "global_writes"
        case sidecarState = "sidecar_state"; case exitCode = "exit_code"
    }
}

struct LearningProposalListPayload: Codable, LearningPayloadMetadata, LearningActionMetadata, Equatable {
    let schemaVersion: Int; let command: String; let action: String; let repo: String
    let proposals: [LearningProposal]; let count: Int; let warnings: [String]
    let targetRepoWrites: LearningWriteMetadata; let sidecarWrites: LearningWriteMetadata; let globalWrites: LearningWriteMetadata
    let sidecarState: LearningSidecarState; let exitCode: Int
    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"; case command, action, repo, proposals, count, warnings
        case targetRepoWrites = "target_repo_writes"; case sidecarWrites = "sidecar_writes"; case globalWrites = "global_writes"
        case sidecarState = "sidecar_state"; case exitCode = "exit_code"
    }
}

struct LearningDecisionListPayload: Codable, LearningPayloadMetadata, LearningActionMetadata, Equatable {
    let schemaVersion: Int; let command: String; let action: String; let repo: String
    let decisions: [LearningDecision]; let count: Int; let warnings: [String]
    let targetRepoWrites: LearningWriteMetadata; let sidecarWrites: LearningWriteMetadata; let globalWrites: LearningWriteMetadata
    let sidecarState: LearningSidecarState; let exitCode: Int
    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"; case command, action, repo, decisions, count, warnings
        case targetRepoWrites = "target_repo_writes"; case sidecarWrites = "sidecar_writes"; case globalWrites = "global_writes"
        case sidecarState = "sidecar_state"; case exitCode = "exit_code"
    }
}

struct LearningContextListPayload: Codable, LearningPayloadMetadata, LearningActionMetadata, Equatable {
    let schemaVersion: Int; let command: String; let action: String; let repo: String
    let contexts: [LearningContext]; let count: Int; let warnings: [String]; let sidecarOnlyGuidance: Bool
    let targetRepoWrites: LearningWriteMetadata; let sidecarWrites: LearningWriteMetadata; let globalWrites: LearningWriteMetadata
    let sidecarState: LearningSidecarState; let exitCode: Int
    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"; case command, action, repo, contexts, count, warnings
        case sidecarOnlyGuidance = "sidecar_only_guidance"
        case targetRepoWrites = "target_repo_writes"; case sidecarWrites = "sidecar_writes"; case globalWrites = "global_writes"
        case sidecarState = "sidecar_state"; case exitCode = "exit_code"
    }
}

typealias LearningThreadSummaryListPayload = LearningEventListPayload

struct LearningUpstreamListPayload: Codable, LearningPayloadMetadata, LearningActionMetadata, Equatable {
    let schemaVersion: Int; let command: String; let action: String; let repo: String
    let candidates: [LearningUpstreamCandidate]; let count: Int; let warnings: [String]; let rolloutGuidance: LearningRolloutGuidance
    let targetRepoWrites: LearningWriteMetadata; let sidecarWrites: LearningWriteMetadata; let globalWrites: LearningWriteMetadata
    let sidecarState: LearningSidecarState; let exitCode: Int
    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"; case command, action, repo, candidates, count, warnings
        case rolloutGuidance = "rollout_guidance"
        case targetRepoWrites = "target_repo_writes"; case sidecarWrites = "sidecar_writes"; case globalWrites = "global_writes"
        case sidecarState = "sidecar_state"; case exitCode = "exit_code"
    }
}

struct LearningUpstreamReconcilePayload: Codable, LearningPayloadMetadata, LearningActionMetadata, Equatable {
    let schemaVersion: Int; let command: String; let action: String; let repo: String
    let candidates: [LearningReconcileCandidate]; let count: Int; let warnings: [String]; let rolloutGuidance: LearningRolloutGuidance
    let targetRepoWrites: LearningWriteMetadata; let sidecarWrites: LearningWriteMetadata; let globalWrites: LearningWriteMetadata
    let sidecarState: LearningSidecarState; let exitCode: Int
    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"; case command, action, repo, candidates, count, warnings
        case rolloutGuidance = "rollout_guidance"
        case targetRepoWrites = "target_repo_writes"; case sidecarWrites = "sidecar_writes"; case globalWrites = "global_writes"
        case sidecarState = "sidecar_state"; case exitCode = "exit_code"
    }
}

struct LearningEvaluationFacts: Codable, Equatable {
    let threadSummaryEvents: Int; let schemaValidEvents: Int; let upstreamCandidates: Int
    enum CodingKeys: String, CodingKey {
        case threadSummaryEvents = "thread_summary_events"
        case schemaValidEvents = "schema_valid_events"
        case upstreamCandidates = "upstream_candidates"
    }
}

struct LearningEvaluationCaveat: Codable, Equatable {
    let notEffectivenessClaim: Bool; let note: String
    enum CodingKeys: String, CodingKey { case notEffectivenessClaim = "not_effectiveness_claim"; case note }
}

struct LearningEvaluatePayload: Codable, LearningPayloadMetadata, LearningActionMetadata, Equatable {
    let schemaVersion: Int; let command: String; let action: String; let repo: String
    let facts: LearningEvaluationFacts; let caveat: LearningEvaluationCaveat; let warnings: [String]; let rolloutGuidance: LearningRolloutGuidance
    let targetRepoWrites: LearningWriteMetadata; let sidecarWrites: LearningWriteMetadata; let globalWrites: LearningWriteMetadata
    let sidecarState: LearningSidecarState; let exitCode: Int
    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"; case command, action, repo, facts, caveat, warnings
        case rolloutGuidance = "rollout_guidance"
        case targetRepoWrites = "target_repo_writes"; case sidecarWrites = "sidecar_writes"; case globalWrites = "global_writes"
        case sidecarState = "sidecar_state"; case exitCode = "exit_code"
    }
}

struct LearningGate: Codable, Equatable { let state: String; let reason: String }

struct LearningErrorPayload: Codable, LearningPayloadMetadata, LearningActionMetadata, Equatable {
    let schemaVersion: Int; let command: String; let action: String; let repo: String; let policyState: String?
    let policy: LearningPolicyStatus?; let learningPaths: LearningPaths?; let gate: LearningGate?; let errors: [String]?
    let targetRepoWrites: LearningWriteMetadata; let sidecarWrites: LearningWriteMetadata; let globalWrites: LearningWriteMetadata
    let sidecarState: LearningSidecarState; let exitCode: Int
    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"; case command, action, repo
        case policyState = "policy_state"; case policy; case learningPaths = "learning_paths"; case gate, errors
        case targetRepoWrites = "target_repo_writes"; case sidecarWrites = "sidecar_writes"; case globalWrites = "global_writes"
        case sidecarState = "sidecar_state"; case exitCode = "exit_code"
    }
}

struct LearningMutationReceipt: Codable, LearningPayloadMetadata, LearningActionMetadata, Equatable {
    let schemaVersion: Int; let command: String; let action: String; let repo: String
    let targetRepoWrites: LearningWriteMetadata; let sidecarWrites: LearningWriteMetadata; let globalWrites: LearningWriteMetadata
    let sidecarState: LearningSidecarState; let exitCode: Int
    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"; case command, action, repo
        case targetRepoWrites = "target_repo_writes"; case sidecarWrites = "sidecar_writes"; case globalWrites = "global_writes"
        case sidecarState = "sidecar_state"; case exitCode = "exit_code"
    }
}

struct LearningEventRecordPayload: Codable, LearningPayloadMetadata, LearningActionMetadata, LearningWriteSuccessMetadata, Equatable {
    let schemaVersion: Int; let command: String; let action: String; let repo: String
    let policyState: String; let policy: LearningPolicyStatus; let gate: LearningGate
    let event: LearningEvent; let eventPath: String
    let targetRepoWrites: LearningWriteMetadata; let sidecarWrites: LearningWriteMetadata; let globalWrites: LearningWriteMetadata
    let sidecarState: LearningSidecarState; let exitCode: Int
    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"; case command, action, repo; case policyState = "policy_state"; case policy, gate, event; case eventPath = "event_path"
        case targetRepoWrites = "target_repo_writes"; case sidecarWrites = "sidecar_writes"; case globalWrites = "global_writes"
        case sidecarState = "sidecar_state"; case exitCode = "exit_code"
    }
}

struct LearningProposalCreatePayload: Codable, LearningPayloadMetadata, LearningActionMetadata, LearningWriteSuccessMetadata, Equatable {
    let schemaVersion: Int; let command: String; let action: String; let repo: String
    let policyState: String; let policy: LearningPolicyStatus; let gate: LearningGate
    let proposal: LearningProposal; let proposalPath: String; let nonExecutionGuarantee: LearningNonExecutionGuarantee
    let targetRepoWrites: LearningWriteMetadata; let sidecarWrites: LearningWriteMetadata; let globalWrites: LearningWriteMetadata
    let sidecarState: LearningSidecarState; let exitCode: Int
    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"; case command, action, repo; case policyState = "policy_state"; case policy, gate, proposal; case proposalPath = "proposal_path"; case nonExecutionGuarantee = "non_execution_guarantee"
        case targetRepoWrites = "target_repo_writes"; case sidecarWrites = "sidecar_writes"; case globalWrites = "global_writes"
        case sidecarState = "sidecar_state"; case exitCode = "exit_code"
    }
}

struct LearningDecisionRecordPayload: Codable, LearningPayloadMetadata, LearningActionMetadata, LearningWriteSuccessMetadata, Equatable {
    let schemaVersion: Int; let command: String; let action: String; let repo: String
    let policyState: String; let policy: LearningPolicyStatus; let gate: LearningGate
    let decision: LearningDecision; let decisionPath: String; let nonExecutionGuarantee: LearningNonExecutionGuarantee
    let targetRepoWrites: LearningWriteMetadata; let sidecarWrites: LearningWriteMetadata; let globalWrites: LearningWriteMetadata
    let sidecarState: LearningSidecarState; let exitCode: Int
    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"; case command, action, repo; case policyState = "policy_state"; case policy, gate, decision; case decisionPath = "decision_path"; case nonExecutionGuarantee = "non_execution_guarantee"
        case targetRepoWrites = "target_repo_writes"; case sidecarWrites = "sidecar_writes"; case globalWrites = "global_writes"
        case sidecarState = "sidecar_state"; case exitCode = "exit_code"
    }
}

struct LearningContextBuildPayload: Codable, LearningPayloadMetadata, LearningActionMetadata, LearningWriteSuccessMetadata, Equatable {
    let schemaVersion: Int; let command: String; let action: String; let repo: String
    let policyState: String; let policy: LearningPolicyStatus; let gate: LearningGate
    let context: LearningContext; let contextPath: String; let nonExecutionGuarantee: LearningNonExecutionGuarantee
    let targetRepoWrites: LearningWriteMetadata; let sidecarWrites: LearningWriteMetadata; let globalWrites: LearningWriteMetadata
    let sidecarState: LearningSidecarState; let exitCode: Int
    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"; case command, action, repo; case policyState = "policy_state"; case policy, gate, context; case contextPath = "context_path"; case nonExecutionGuarantee = "non_execution_guarantee"
        case targetRepoWrites = "target_repo_writes"; case sidecarWrites = "sidecar_writes"; case globalWrites = "global_writes"
        case sidecarState = "sidecar_state"; case exitCode = "exit_code"
    }
}

struct LearningThreadSummaryInputContract: Codable, Equatable {
    let schema: String; let rawTranscriptScan: Bool; let historyMining: Bool; let networkCalls: Bool; let note: String
    enum CodingKeys: String, CodingKey {
        case schema; case rawTranscriptScan = "raw_transcript_scan"; case historyMining = "history_mining"; case networkCalls = "network_calls"; case note
    }
}

struct LearningThreadSummaryImportPayload: Codable, LearningPayloadMetadata, LearningActionMetadata, LearningWriteSuccessMetadata, Equatable {
    let schemaVersion: Int; let command: String; let action: String; let repo: String
    let policyState: String; let policy: LearningPolicyStatus; let gate: LearningGate
    let event: LearningEvent; let eventPath: String
    let inputContract: LearningThreadSummaryInputContract
    let targetRepoWrites: LearningWriteMetadata; let sidecarWrites: LearningWriteMetadata; let globalWrites: LearningWriteMetadata
    let sidecarState: LearningSidecarState; let exitCode: Int
    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"; case command, action, repo; case policyState = "policy_state"; case policy, gate, event; case eventPath = "event_path"; case inputContract = "input_contract"
        case targetRepoWrites = "target_repo_writes"; case sidecarWrites = "sidecar_writes"; case globalWrites = "global_writes"
        case sidecarState = "sidecar_state"; case exitCode = "exit_code"
    }
}

struct LearningUpstreamExportPayload: Codable, LearningPayloadMetadata, LearningActionMetadata, LearningWriteSuccessMetadata, Equatable {
    let schemaVersion: Int; let command: String; let action: String; let repo: String
    let policyState: String; let policy: LearningPolicyStatus; let gate: LearningGate
    let candidate: LearningUpstreamCandidate; let candidatePath: String
    let rolloutGuidance: LearningRolloutGuidance
    let targetRepoWrites: LearningWriteMetadata; let sidecarWrites: LearningWriteMetadata; let globalWrites: LearningWriteMetadata
    let sidecarState: LearningSidecarState; let exitCode: Int
    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"; case command, action, repo; case policyState = "policy_state"; case policy, gate, candidate; case candidatePath = "candidate_path"; case rolloutGuidance = "rollout_guidance"
        case targetRepoWrites = "target_repo_writes"; case sidecarWrites = "sidecar_writes"; case globalWrites = "global_writes"
        case sidecarState = "sidecar_state"; case exitCode = "exit_code"
    }
}

enum LearningPayloadValidationError: LocalizedError, Equatable {
    case invalid(String)
    var errorDescription: String? {
        switch self { case .invalid(let reason): return "Learning payload rejected: \(reason)" }
    }
}

enum LearningPayloadValidator {
    static func validate<T: LearningPayloadMetadata>(
        _ payload: T,
        expectedCommand: LearningCommandRoute,
        selectedRepo: String,
        environment: [String: String] = ProcessInfo.processInfo.environment
    ) throws {
        guard payload.schemaVersion == 1 else { throw LearningPayloadValidationError.invalid("schema_version must be 1") }
        guard payload.command == expectedCommand.rawValue else { throw LearningPayloadValidationError.invalid("command metadata mismatch") }
        guard payload.exitCode == 0 else { throw LearningPayloadValidationError.invalid("success payload has non-zero exit metadata") }
        let expectedIdentity = sidecarRepoIdentity(selectedRepo: selectedRepo)
        guard selectedRepo.hasPrefix("/"), resolvedExistingOrLexical(payload.repo) == expectedIdentity.root else {
            throw LearningPayloadValidationError.invalid("repo metadata does not match the selected repository")
        }
        if let actionPayload = payload as? any LearningActionMetadata {
            guard actionPayload.action != "error" else {
                throw LearningPayloadValidationError.invalid("error action cannot be accepted as success")
            }
        }
        let expectedSidecarRoot = expectedSidecarStateDirectory(selectedRepo: selectedRepo, environment: environment)
        // `learn status` reports a future directory that normally does not exist yet.
        // Preserve the CLI's lexical spelling here; resolving it through Foundation
        // rewrites Darwin's /private/tmp identity to /tmp.
        let sidecarRoot = lexicalAbsolutePath(payload.sidecarState.repoStateDir)
        guard payload.sidecarState.repoStateDir.hasPrefix("/"), sidecarRoot == expectedSidecarRoot else {
            throw LearningPayloadValidationError.invalid("sidecar state directory does not match the selected repository")
        }
        let repoIdentity = payload.sidecarState.repo
        guard repoIdentity.root.hasPrefix("/"),
              resolvedExistingOrLexical(repoIdentity.root) == expectedIdentity.root,
              repoIdentity.hash == expectedIdentity.hash,
              repoIdentity.id == expectedIdentity.id else {
            throw LearningPayloadValidationError.invalid("sidecar repository identity does not match the selected repository")
        }
        try requireNoWrites(payload.targetRepoWrites, label: "target")
        try requireNoWrites(payload.globalWrites, label: "global")

        if let status = payload as? LearningStatusPayload, status.policyState == "active" {
            try requireActiveTargetPolicy(state: status.policyState, policy: status.policy)
        }
        if expectedCommand.writesSidecar {
            guard let writePayload = payload as? any LearningWriteSuccessMetadata else {
                throw LearningPayloadValidationError.invalid("write success omitted policy and gate metadata")
            }
            try requireActiveTargetPolicy(state: writePayload.policyState, policy: writePayload.policy)
            guard writePayload.gate.state == "approved" else {
                throw LearningPayloadValidationError.invalid("write success gate must be approved")
            }
            guard payload.sidecarWrites.performed, !payload.sidecarWrites.paths.isEmpty else {
                throw LearningPayloadValidationError.invalid("write success did not report sidecar writes")
            }
            guard payload.sidecarWrites.paths.allSatisfy({ contains(path: $0, in: sidecarRoot) }) else {
                throw LearningPayloadValidationError.invalid("sidecar write escaped the repository sidecar")
            }
        } else {
            try requireNoWrites(payload.sidecarWrites, label: "sidecar")
        }
        try validateReturnedRecords(payload, selectedRepo: selectedRepo)
    }

    private static func requireActiveTargetPolicy(state: String, policy: LearningPolicyStatus) throws {
        guard state == "active", policy.state == "active", policy.enabled == true,
              policy.ownership == "target", policy.policyID == "supervised-learning", policy.schemaVersion == 1 else {
            throw LearningPayloadValidationError.invalid("write success requires an active target-owned supervised-learning policy")
        }
    }

    private static func validateReturnedRecords<T>(_ payload: T, selectedRepo: String) throws {
        if let value = payload as? LearningEventListPayload {
            try value.events.forEach { try validateEvent($0, selectedRepo: selectedRepo) }
        }
        if let value = payload as? LearningEventRecordPayload {
            try validateEvent(value.event, selectedRepo: selectedRepo)
        }
        if let value = payload as? LearningThreadSummaryImportPayload {
            try validateEvent(value.event, selectedRepo: selectedRepo)
            guard value.event.provenance.capture == "thread-summary-import",
                  !value.inputContract.rawTranscriptScan, !value.inputContract.historyMining, !value.inputContract.networkCalls else {
                throw LearningPayloadValidationError.invalid("thread-summary import contract must remain bounded and non-mining")
            }
        }
        if let value = payload as? LearningProposalListPayload {
            try value.proposals.forEach { try validateProposal($0, selectedRepo: selectedRepo) }
        }
        if let value = payload as? LearningProposalCreatePayload {
            try validateProposal(value.proposal, selectedRepo: selectedRepo)
            try requireNonExecution(value.nonExecutionGuarantee)
        }
        if let value = payload as? LearningDecisionListPayload {
            try value.decisions.forEach { try validateDecision($0, selectedRepo: selectedRepo) }
        }
        if let value = payload as? LearningDecisionRecordPayload {
            try validateDecision(value.decision, selectedRepo: selectedRepo)
            try requireNonExecution(value.nonExecutionGuarantee)
        }
        if let value = payload as? LearningContextListPayload {
            try value.contexts.forEach { try validateContext($0, selectedRepo: selectedRepo) }
        }
        if let value = payload as? LearningContextBuildPayload {
            try validateContext(value.context, selectedRepo: selectedRepo)
            try requireNonExecution(value.nonExecutionGuarantee)
        }
        if let value = payload as? LearningUpstreamListPayload {
            try value.candidates.forEach(validateCandidate)
            try requireReviewOnly(value.rolloutGuidance)
        }
        if let value = payload as? LearningUpstreamExportPayload {
            try validateCandidate(value.candidate)
            try requireReviewOnly(value.rolloutGuidance)
        }
        if let value = payload as? LearningUpstreamReconcilePayload {
            try requireReviewOnly(value.rolloutGuidance)
        }
        if let value = payload as? LearningEvaluatePayload {
            try requireReviewOnly(value.rolloutGuidance)
        }
    }

    private static func validateEvent(_ event: LearningEvent, selectedRepo: String) throws {
        guard event.schemaVersion == 1, stableID(event.eventID, prefix: "evt-"), event.policyID == "supervised-learning",
              resolvedExistingOrLexical(event.repo) == resolvedExistingOrLexical(selectedRepo),
              event.supervision == LearningSupervision(humanApprovalRequired: true, approvalState: "approved", approvalFlag: true) else {
            throw LearningPayloadValidationError.invalid("learning event is not an approved supervised record for the selected repository")
        }
    }

    private static func validateProposal(_ proposal: LearningProposal, selectedRepo: String) throws {
        guard proposal.schemaVersion == 1, stableID(proposal.proposalID, prefix: "prop-"), proposal.policyID == "supervised-learning",
              resolvedExistingOrLexical(proposal.repo) == resolvedExistingOrLexical(selectedRepo), proposal.humanApprovalRequired else {
            throw LearningPayloadValidationError.invalid("learning proposal is not a supervised review record for the selected repository")
        }
        try requireNonExecution(proposal.nonExecutionGuarantee)
    }

    private static func validateDecision(_ decision: LearningDecision, selectedRepo: String) throws {
        guard decision.schemaVersion == 1, stableID(decision.decisionID, prefix: "dec-"), decision.policyID == "supervised-learning",
              resolvedExistingOrLexical(decision.repo) == resolvedExistingOrLexical(selectedRepo), decision.humanReview.required,
              decision.humanReview.confirmed, decision.humanReview.capture == "explicit-cli-input" else {
            throw LearningPayloadValidationError.invalid("learning decision lacks confirmed explicit human review for the selected repository")
        }
        try requireNonExecution(decision.nonExecutionGuarantee)
    }

    private static func validateContext(_ context: LearningContext, selectedRepo: String) throws {
        guard context.schemaVersion == 1, stableID(context.contextID, prefix: "ctx-"), context.policyID == "supervised-learning",
              resolvedExistingOrLexical(context.repo) == resolvedExistingOrLexical(selectedRepo), context.sidecarOnlyGuidance else {
            throw LearningPayloadValidationError.invalid("learning context is not sidecar-only guidance for the selected repository")
        }
        try requireNonExecution(context.nonExecutionGuarantee)
    }

    private static func validateCandidate(_ candidate: LearningUpstreamCandidate) throws {
        guard candidate.schemaVersion == 1, stableID(candidate.candidateID, prefix: "upc-"),
              candidate.policyID == "supervised-learning", candidate.redactionConfirmed, candidate.privacyLabel.isExportable else {
            throw LearningPayloadValidationError.invalid("upstream candidate is not a redacted review-only record")
        }
    }

    private static func requireNonExecution(_ guarantee: LearningNonExecutionGuarantee) throws {
        let prohibited = Set(["AGENTS.md", "policy files", "target files", "global tool state"])
        guard guarantee.enforced, !guarantee.recommendationExecutionPermitted,
              Set(guarantee.prohibitedWrites) == prohibited else {
            throw LearningPayloadValidationError.invalid("record does not preserve the CLI non-execution guarantee")
        }
    }

    private static func requireReviewOnly(_ guidance: LearningRolloutGuidance) throws {
        guard guidance.sourceReviewRequired, !guidance.automaticPropagation else {
            throw LearningPayloadValidationError.invalid("upstream guidance must require source review and prohibit automatic propagation")
        }
    }

    private static func requireNoWrites(_ metadata: LearningWriteMetadata, label: String) throws {
        guard !metadata.performed, metadata.paths.isEmpty else {
            throw LearningPayloadValidationError.invalid("\(label) writes must be false and empty")
        }
    }

    static func sidecarRepoIdentity(selectedRepo: String) -> LearningSidecarRepoIdentity {
        let root = resolvedExistingOrLexical(selectedRepo)
        let hash = SHA256.hash(data: Data(root.utf8)).map { String(format: "%02x", $0) }.joined()
        return LearningSidecarRepoIdentity(root: root, hash: hash, id: String(hash.prefix(16)))
    }

    static func expectedSidecarStateDirectory(
        selectedRepo: String,
        environment: [String: String] = ProcessInfo.processInfo.environment
    ) -> String {
        let home = environment["HOME"].flatMap { $0.isEmpty ? nil : $0 } ?? NSHomeDirectory()
        let base: String
        if let xdgStateHome = environment["XDG_STATE_HOME"], !xdgStateHome.isEmpty {
            base = resolvedExistingOrLexical(expandingHome(in: xdgStateHome, home: home)) + "/repo-contract-kit"
        } else {
            base = resolvedExistingOrLexical(home) + "/.local/state/repo-contract-kit"
        }
        let identity = sidecarRepoIdentity(selectedRepo: selectedRepo)
        let name = identity.root.split(separator: "/").last.map(String.init) ?? "repo"
        let slug = name.replacingOccurrences(of: "[^A-Za-z0-9._-]+", with: "-", options: .regularExpression)
            .trimmingCharacters(in: CharacterSet(charactersIn: ".-"))
        return base + "/\(slug.isEmpty ? "repo" : slug)-\(identity.id)"
    }

    private static func resolvedExistingOrLexical(_ path: String) -> String {
        let lexical = lexicalAbsolutePath(path)
        return posixRealpath(lexical) ?? lexical
    }

    private static func posixRealpath(_ path: String) -> String? {
        var buffer = [CChar](repeating: 0, count: Int(PATH_MAX))
        return path.withCString { input in
            buffer.withUnsafeMutableBufferPointer { output in
                guard let resolved = Darwin.realpath(input, output.baseAddress) else { return nil }
                return String(cString: resolved)
            }
        }
    }

    private static func lexicalAbsolutePath(_ path: String) -> String {
        guard path.hasPrefix("/") else { return path }
        var components = [Substring]()
        for component in path.split(separator: "/", omittingEmptySubsequences: true) {
            switch component {
            case ".":
                continue
            case "..":
                if !components.isEmpty { components.removeLast() }
            default:
                components.append(component)
            }
        }
        return "/" + components.map(String.init).joined(separator: "/")
    }
    private static func expandingHome(in path: String, home: String) -> String {
        if path == "~" { return home }
        if path.hasPrefix("~/") { return home + String(path.dropFirst()) }
        return path
    }
    private static func stableID(_ value: String, prefix: String) -> Bool {
        guard value.hasPrefix(prefix), value.count == prefix.count + 20 else { return false }
        return value.dropFirst(prefix.count).allSatisfy { character in
            ("0"..."9").contains(String(character)) || ("a"..."f").contains(String(character))
        }
    }
    private static func contains(path: String, in root: String) -> Bool {
        // Write receipts must name existing artifacts. Resolve both sides when
        // possible so a symlink inside the state directory cannot escape it.
        let value = resolvedExistingOrLexical(path)
        let containmentRoot = resolvedExistingOrLexical(root)
        return value == containmentRoot || value.hasPrefix(containmentRoot + "/")
    }
}

struct LearningThreadSummaryInput: Codable, Equatable {
    struct Redaction: Codable, Equatable {
        let humanConfirmed: Bool
        let rawTranscriptExcluded: Bool
        let rawFeedbackExcluded: Bool
        let rawEventContentExcluded: Bool
        let privateContentExcluded: Bool
        enum CodingKeys: String, CodingKey {
            case humanConfirmed = "human_confirmed"; case rawTranscriptExcluded = "raw_transcript_excluded"
            case rawFeedbackExcluded = "raw_feedback_excluded"; case rawEventContentExcluded = "raw_event_content_excluded"
            case privateContentExcluded = "private_content_excluded"
        }
    }
    struct OutcomeCounts: Codable, Equatable { let confirmed: Int; let inconclusive: Int; let regressed: Int }
    struct Aggregate: Codable, Equatable {
        let interactionCount: Int; let outcomeCounts: OutcomeCounts; let classificationCounts: [String: Int]; let redactedSummary: String
        enum CodingKeys: String, CodingKey {
            case interactionCount = "interaction_count"; case outcomeCounts = "outcome_counts"
            case classificationCounts = "classification_counts"; case redactedSummary = "redacted_summary"
        }
    }
    let schemaVersion: Int; let summaryID: String; let reportedAt: String; let redaction: Redaction; let aggregate: Aggregate
    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"; case summaryID = "summary_id"; case reportedAt = "reported_at"; case redaction, aggregate
    }

    static func loadStrict(from url: URL) throws -> LearningThreadSummaryInput {
        let values = try url.resourceValues(forKeys: [.isRegularFileKey, .fileSizeKey])
        guard values.isRegularFile == true, (values.fileSize ?? 4097) <= 4096 else {
            throw LearningPayloadValidationError.invalid("thread-summary input must be a regular JSON file no larger than 4096 bytes")
        }
        let data = try Data(contentsOf: url)
        let object = try JSONSerialization.jsonObject(with: data)
        guard let root = object as? [String: Any], Set(root.keys) == ["schema_version", "summary_id", "reported_at", "redaction", "aggregate"],
              let redaction = root["redaction"] as? [String: Any], Set(redaction.keys) == ["human_confirmed", "raw_transcript_excluded", "raw_feedback_excluded", "raw_event_content_excluded", "private_content_excluded"],
              let aggregate = root["aggregate"] as? [String: Any], Set(aggregate.keys) == ["interaction_count", "outcome_counts", "classification_counts", "redacted_summary"],
              let outcomes = aggregate["outcome_counts"] as? [String: Any], Set(outcomes.keys) == ["confirmed", "inconclusive", "regressed"] else {
            throw LearningPayloadValidationError.invalid("thread-summary fields must match the strict schema exactly")
        }
        let input = try JSONDecoder().decode(LearningThreadSummaryInput.self, from: data)
        try input.validate()
        return input
    }

    func validate() throws {
        let outcomeCounts = [aggregate.outcomeCounts.confirmed, aggregate.outcomeCounts.inconclusive, aggregate.outcomeCounts.regressed]
        let classificationValues = Array(aggregate.classificationCounts.values)
        let allowedClassifications = Set(LearningProposalClassification.allCases.map(\.rawValue))
        guard schemaVersion == 1,
              Self.stableSummaryID(summaryID), Self.validUTCTimestamp(reportedAt),
              redaction == Redaction(humanConfirmed: true, rawTranscriptExcluded: true, rawFeedbackExcluded: true, rawEventContentExcluded: true, privateContentExcluded: true),
              (1...10_000).contains(aggregate.interactionCount),
              outcomeCounts.allSatisfy({ (0...10_000).contains($0) }),
              outcomeCounts.reduce(0, +) == aggregate.interactionCount,
              !aggregate.classificationCounts.isEmpty,
              aggregate.classificationCounts.count <= allowedClassifications.count,
              Set(aggregate.classificationCounts.keys).isSubset(of: allowedClassifications),
              classificationValues.allSatisfy({ (0...10_000).contains($0) }),
              classificationValues.reduce(0, +) == aggregate.interactionCount,
              !aggregate.redactedSummary.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
              aggregate.redactedSummary.count <= 300 else {
            throw LearningPayloadValidationError.invalid("thread-summary aggregate or redaction confirmation is invalid")
        }
    }

    func writeTemporary(fileManager: FileManager = .default) throws -> URL {
        try validate()
        let url = fileManager.temporaryDirectory.appendingPathComponent("KitCompanion-Learning-\(UUID().uuidString).json")
        let encoder = JSONEncoder(); encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        let data = try encoder.encode(self)
        var descriptor = url.path.withCString { Darwin.open($0, O_WRONLY | O_CREAT | O_EXCL, 0o600) }
        guard descriptor >= 0 else { throw Self.posixError() }
        var removeOnFailure = true
        defer {
            if descriptor >= 0 { Darwin.close(descriptor) }
            if removeOnFailure { try? fileManager.removeItem(at: url) }
        }

        try data.withUnsafeBytes { rawBuffer in
            guard let base = rawBuffer.baseAddress else { return }
            var offset = 0
            while offset < rawBuffer.count {
                let written = Darwin.write(descriptor, base.advanced(by: offset), rawBuffer.count - offset)
                guard written > 0 else { throw Self.posixError() }
                offset += written
            }
        }
        guard Darwin.fsync(descriptor) == 0 else { throw Self.posixError() }
        guard Darwin.close(descriptor) == 0 else {
            descriptor = -1
            throw Self.posixError()
        }
        descriptor = -1
        removeOnFailure = false
        return url
    }

    private static func stableSummaryID(_ value: String) -> Bool {
        guard value.hasPrefix("tsum-"), value.count == 25 else { return false }
        return value.dropFirst(5).allSatisfy { character in
            ("0"..."9").contains(String(character)) || ("a"..."f").contains(String(character))
        }
    }

    private static func validUTCTimestamp(_ value: String) -> Bool {
        guard value.range(of: #"^\S+T\S+Z$"#, options: .regularExpression) != nil else { return false }
        let standard = ISO8601DateFormatter()
        standard.formatOptions = [.withInternetDateTime]
        if standard.date(from: value) != nil { return true }
        let fractional = ISO8601DateFormatter()
        fractional.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return fractional.date(from: value) != nil
    }

    private static func posixError() -> NSError {
        NSError(domain: NSPOSIXErrorDomain, code: Int(errno), userInfo: nil)
    }
}
