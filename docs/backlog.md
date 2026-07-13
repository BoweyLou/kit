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
recommendation. Receipt linkage remains deferred.

## Phase 4 — Context and retention integration (shipped)

`kit learn context build --decision-id <dec-id>` is policy-gated and succeeds
only for an existing local schema-valid `approved` decision whose linked local
proposal remains valid and approved. It creates a sidecar-only `ctx-` record
with only decision/proposal IDs, classification, scope, recommended change,
privacy label, retention expiry, and the no-execution guarantee. It never
copies raw event, evidence, feedback, or conversation content. Rejected,
deferred, missing, invalid, stale, or mismatched lineage fails before any new
sidecar state is created.

`kit learn context list` is read-only and returns only contexts whose structure
and current local decision/proposal lineage still prove an approved decision
for the selected repository. `kit agent-context-bundle` exposes the same valid
records under a low deterministic cap as sidecar-only guidance, not target
instructions. It does not execute recommendations or alter agent instructions.

`kit task-packet --learning-decision <dec-id>` may record explicitly requested
approved local decision IDs as artifact lineage after validating every ID before
its optional sidecar write. Receipt and target task mechanics remain unchanged.
`kit retention --json` reports learning artifact counts and a context-expiry
preview only; Phase 4 adds no deletion command.

## Phase 5 — Evaluation and governed rollout

`kit learn thread-summary import --input <file> --approved` accepts only one
strict bounded, explicitly redacted aggregate summary file under an active
supervised target policy. It does not scan runtime state, mine Codex history,
read transcripts or feedback/event content, or call a network. A valid import
writes exactly one derived sidecar event with `thread-summary-import`
provenance; rejected, unapproved, unredacted, oversized, private, or unsupported
input writes nothing.

`kit learn upstream export` creates one portable local sidecar candidate only
from a currently schema-valid approved decision and its matching approved
proposal. It requires `--redaction-confirmed` and `public-ok` or `internal`
privacy. Candidates contain only bounded recommendation/classification/scope,
decision/proposal IDs, a sanitized origin, and source-ref/version baseline;
they exclude event IDs, raw summaries, evidence, feedback, context, and raw
repository paths. List, reconcile, and evaluate routes are read-only; they
revalidate candidate lineage and mark revalidation when the current local tool
source has advanced.

An upstream candidate is a source-review input, not a propagation mechanism.
Review it through a normal source task, commit, test, and release. Only after
that release may a human run `kit self update`, followed by a guarded target
update or reconcile. Broader enablement remains a human decision and must not
be added to default presets implicitly.

## Phase 6 — Kit Companion Learning dashboard (shipped)

Add Learning as the fifth optional macOS dashboard section with typed read
models for policy/status, counts, review queues, histories, reconciliation, and
evaluation. Launch and Refresh are read-only. Profile setup and policy changes
remain Terminal-only, and Command Browser remains the discovery/copy fallback.

The app permits exactly six confirmation-gated sidecar writes: event record,
proposal create, decision record, context build, strict redacted thread-summary
import through a private temporary file, and sanitized upstream source-review
candidate export. The generic runner rejects the complete `learn` namespace;
the typed Learning runner rejects unknown routes, flags, repos, and payloads.
No learning app action writes target/global state, mines history, executes a
recommendation, updates source or targets, pushes, releases, or propagates a
candidate.
