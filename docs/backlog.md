# Supervised Learning Backlog

This backlog stages supervised learning as a local, reviewable capability. Each
phase preserves the target repository boundary and requires explicit approval
before any new write surface is introduced.

## Phase 1 — Foundation and ownership contract

Ship the opt-in `supervised-learning` profile, target-owned policy, canonical
and installed schemas, ownership ADR, and read-only `kit learn status`. The
status command reports policy state, future learning paths, safe next commands,
and explicit false target, sidecar, and global write guarantees. No event,
proposal, decision, or context write commands exist in this phase.

## Phase 2 — Supervised event capture (shipped)

`kit learn event record` writes one explicit, schema-validated local sidecar
record only after the installed target-owned policy is enabled and a human
passes `--approved`. `kit learn event list` is read-only. Records carry stable
event IDs, timestamps, provenance, privacy labels, outcomes, and bounded
explicit text; Kit does not harvest conversations or feedback. Rejected,
unapproved, disabled, invalid, and unenrolled attempts write no target,
sidecar, or global state.

## Phase 3 — Reviewable proposals and decisions (shipped)

`kit learn proposal create` accepts bounded explicit CLI text and existing
schema-valid local event IDs only, stores a stable-ID proposal in this target's
sidecar, and begins it as `pending-review`. `kit learn proposal list` is
read-only. Proposal records retain scope, classification, recommendation,
event lineage, and privacy labels.

`kit learn decision record` requires an existing `pending-review` proposal,
`--human-review-confirmed`, a named decider, non-empty rationale, and an
approved/rejected/deferred outcome. It stores a stable-ID decision in the
sidecar and updates the linked proposal state; `kit learn decision list` is
read-only. Disabled or uninstalled policies, invalid/missing evidence,
missing/non-pending proposals, missing review confirmation, and invalid fields
write no state.

An approved proposal or decision is never permission to modify AGENTS.md,
policy files, target files, or global Kit state, and Kit does not execute a
recommendation. Task-packet and receipt linkage remain deferred.

## Phase 4 — Context and retention integration

Add bounded context retrieval and retention controls for approved sidecar
records. Privacy labels, redaction, and purge previews must remain local-first
and preserve evidence needed for decisions.

## Phase 5 — Evaluation and governed rollout

Evaluate the workflow across opted-in repositories, document safety and utility
evidence, and define a governed rollout path. Broader enablement remains a
human decision; it must not be added to default presets implicitly.
