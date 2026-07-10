# ADR 0005: Supervised Learning Ownership Boundaries

## Status

Accepted

## Context

Learning artifacts can be useful for improving local operator workflows, but
they may contain private context, uncertain recommendations, or information
that should not become source code, Git history, or global tool state. The
first delivery must establish where each artifact belongs before any command is
allowed to create one.

## Decision

Use a three-surface ownership model.

- The target repository owns `.agent-workflows/learning-policy.json`. The
  `supervised-learning` profile may create the initial policy, but later Kit
  updates preserve target changes. The policy requires human approval and is
  opt-in only; no default preset includes the profile.
- Kit owns the canonical schemas in `workflows/schemas/` and their installed
  `templates/common/` mirrors. Targets receive the schemas under `schemas/` as
  managed contract files.
- Learning events, proposals, decisions, and context belong in the
  repository-specific local Kit sidecar. They are not target-repository files
  and are not global tool configuration. Their paths may be reported without
  creating sidecar directories.

`kit learn status --repo <repo> --json` remains read-only and returns policy
state, target and sidecar paths, safe next commands, and explicit false target,
sidecar, and global write guarantees.

Phase 2 adds `kit learn event record` and `kit learn event list`. A record is
permitted only when the target has the installed `supervised-learning` profile,
its target-owned policy is enabled and supervised, and the exact invocation
passes `--approved`. The record must validate against the learning-event
contract before Kit creates the sidecar. It includes a stable event ID,
timestamp, explicit CLI provenance source, policy-derived or explicit privacy
label, bounded explicit summary/evidence, outcome, and approved supervision.
`list` reads only valid local event files and never creates a sidecar. Neither
command writes target files or global Kit configuration; rejected, unapproved,
invalid, disabled, or unenrolled record attempts write nothing.

No event command reads conversations, feedback ledgers, thread history, or
other implicit inputs. Phase 2 still provides no proposal, decision, or context
write commands, and no learning command can modify the target repository or
global tool checkout.

Phase 3 adds `kit learn proposal create`/`list` and `kit learn decision
record`/`list`. Proposal creation remains policy-gated and accepts only bounded
explicit CLI fields plus existing schema-valid local event IDs. Proposal records
have stable IDs, scope and classification, bounded recommendations, privacy,
and event lineage; they start `pending-review`. Decision recording requires an
existing pending proposal, `--human-review-confirmed`, a named decider, and a
non-empty rationale. It records approved/rejected/deferred state in the
sidecar and updates the linked proposal. List commands are read-only.

Phase 3 approval is a review state, not execution authority. Neither an
accepted proposal nor an approved decision may modify AGENTS.md, policy files,
target files, or global Kit state, and Kit must not execute recommendations.
Receipt linkage remains deferred. Disabled/uninstalled policy, invalid or
missing evidence, missing/non-pending proposals, missing human review
confirmation, and invalid fields must fail before sidecar initialization and
write nothing.

Phase 4 adds `kit learn context build`/`list`. Building context remains
policy-gated and requires an existing schema-valid local `approved` decision
and the decision's schema-valid linked proposal in approved state. The builder
constructs a stable-ID sidecar record from an explicit allowlist only:
decision/proposal IDs, classification, scope, recommended change, privacy
label, retention expiry, and the existing no-execution guarantee. It excludes
event IDs, raw event/evidence, feedback, rationale, decider, follow-up, and
conversation content. `list` and `kit agent-context-bundle` revalidate the
stored decision/proposal link for the selected repo and skip stale or
hand-crafted contexts with a warning. The bundle holds a low deterministic cap
and labels the result sidecar-only guidance, not target instructions.

Phase 4 also allows `kit task-packet --learning-decision <dec-id>` to retain
only explicitly requested schema-valid approved decision IDs in the packet
artifact. Every requested ID is validated before the existing optional packet
sidecar write. This is lineage only: it changes neither target task files nor
receipt mechanics, and it does not authorize execution. `kit retention --json`
reports learning counts and a context expiry preview without deleting anything.

## Consequences

Operators can inspect the foundation safely before opting in. Target-specific
approval and retention choices stay reviewable in the target policy, while
potentially sensitive artifacts remain local to the target's sidecar and are
recorded only through explicit approved input.

Future phases must add a new ADR or amend this one before broadening writes,
changing ownership, adding a default preset, allowing automatic capture or
context injection beyond the bounded sidecar-only bundle section, changing
receipt mechanics, adding deletion, or allowing a learning record to trigger a
target/global action.
