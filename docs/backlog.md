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

## Phase 2 — Supervised event capture

Design and test an explicit event-capture workflow that writes only approved,
schema-validated sidecar records. It must preserve the target policy boundary,
record approval state, and remain opt-in.

## Phase 3 — Reviewable proposals and decisions

Introduce proposal and decision records only with a human review gate,
traceable evidence, and a clear separation between recommendation and action.
No accepted proposal may change target files or global configuration by itself.

## Phase 4 — Context and retention integration

Add bounded context retrieval and retention controls for approved sidecar
records. Privacy labels, redaction, and purge previews must remain local-first
and preserve evidence needed for decisions.

## Phase 5 — Evaluation and governed rollout

Evaluate the workflow across opted-in repositories, document safety and utility
evidence, and define a governed rollout path. Broader enablement remains a
human decision; it must not be added to default presets implicitly.
