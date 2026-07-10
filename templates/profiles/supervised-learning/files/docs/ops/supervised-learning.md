# Supervised Learning Policy

This repository opted into the `supervised-learning` profile. Its policy is
target-owned: maintain it for this repository's approval, privacy, and
retention needs. Kit installs the initial file but does not overwrite it during
updates.

Use `kit learn status --json` to inspect the policy, installed schemas, and
sidecar locations. The command is read-only. It creates no target files,
sidecar directories, or global tool state.

Phase 2 permits explicitly approved event capture. Use `kit learn event
record` with `--kind`, bounded `--summary`/optional `--evidence`, `--outcome`,
`--source`, and `--approved` only after a human approves that exact record.
The command requires this installed enabled policy, validates the record before
writing, and stores it only in this repository's local sidecar. `kit learn
event list --json` is read-only.

Phase 3 adds reviewable proposals and human decisions. `kit learn proposal
create` accepts only bounded explicit CLI text and existing schema-valid local
event IDs as evidence; every proposal starts `pending-review`. Use `kit learn
proposal list --json` to inspect valid local proposals without writing state.

`kit learn decision record` requires one existing `pending-review` proposal,
a named decider, non-empty rationale, an approved/rejected/deferred outcome,
and `--human-review-confirmed` after explicit human review. It writes a local
decision record and updates the linked proposal state. `kit learn decision
list --json` is read-only.

An approved proposal or decision is a recorded review outcome only. It does
not authorize changes to AGENTS.md, policy files, target files, or global Kit
state, and Kit does not execute its recommendation. Receipt linkage remains
deferred to a later phase.

Phase 4 adds bounded approved-learning context. `kit learn context build
--decision-id <dec-id> --json` requires an existing local schema-valid approved
decision and its linked valid approved proposal. It stores a sidecar context
record built only from stable decision/proposal IDs, classification, scope,
recommended change, privacy label, retention expiry, and no-execution
guarantee. It never copies event IDs, raw event/evidence, feedback, rationale,
decider, follow-up, or conversation content. `kit learn context list --json`
is read-only and skips stale or hand-crafted contexts whose current local
decision/proposal lineage no longer proves approval.

`make agent-context-bundle` may expose a small deterministic set of valid
approved-learning contexts. They are sidecar-only guidance, not target
instructions, and never execute recommendations. `kit task-packet
--learning-decision <dec-id>` may retain explicitly requested valid approved
decision IDs as sidecar packet lineage, without changing target task files or
receipt mechanics. `kit retention --json` previews learning counts and context
expiry only; it does not delete learning artifacts.

Rejected, unapproved, invalid, disabled, or unenrolled attempts create no
sidecar, target, or global state. Kit never harvests conversations or feedback
text, and it does not reinterpret the separate `kit feedback` ledger.

Learning records belong in the repository's local Kit sidecar, not in source
code, Git history, or global tool configuration. The installed schemas under
`schemas/` define the portable record shapes.
