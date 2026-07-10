# Supervised Learning Policy

This repository opted into the `supervised-learning` profile. Its policy is
target-owned: maintain it for this repository's approval, privacy, and
retention needs. Kit installs the initial file but does not overwrite it during
updates.

Use `kit learn status --json` to inspect the policy, installed schemas, and
sidecar locations. The command is read-only. It creates no target files,
sidecar directories, or global tool state.

Phase 2 permits only explicitly approved event capture. Use `kit learn event
record` with `--kind`, bounded `--summary`/optional `--evidence`, `--outcome`,
`--source`, and `--approved` only after a human approves that exact record.
The command requires this installed enabled policy, validates the record before
writing, and stores it only in this repository's local sidecar. `kit learn
event list --json` is read-only.

Rejected, unapproved, invalid, disabled, or unenrolled attempts create no
sidecar, target, or global state. Kit never harvests conversations or feedback
text, and it does not reinterpret the separate `kit feedback` ledger.

Learning records belong in the repository's local Kit sidecar, not in source
code, Git history, or global tool configuration. The installed schemas under
`schemas/` define the portable record shapes. Proposals, decisions, and context
remain deferred.
