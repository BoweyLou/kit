# Supervised Learning Policy

This repository opted into the `supervised-learning` profile. Its policy is
target-owned: maintain it for this repository's approval, privacy, and
retention needs. Kit installs the initial file but does not overwrite it during
updates.

Use `kit learn status --json` to inspect the policy, installed schemas, and
future sidecar locations. The command is read-only. It creates no target files,
sidecar directories, or global tool state.

Phase 1 deliberately provides no commands that write learning events,
proposals, decisions, or context. Do not create those records from an agent
without a later approved workflow and the human approval required by the local
policy.

Learning records belong in the repository's local Kit sidecar, not in source
code, Git history, or global tool configuration. The installed schemas under
`schemas/` define the portable record shapes for later phases.
