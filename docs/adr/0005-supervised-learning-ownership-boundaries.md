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
- Future learning events, proposals, decisions, and context belong in the
  repository-specific local Kit sidecar. They are not target-repository files
  and are not global tool configuration. Their paths may be reported without
  creating sidecar directories.

`kit learn status --repo <repo> --json` is the sole Phase 1 CLI surface. It is
read-only and returns policy state, target and future sidecar paths, safe next
commands, and explicit false target, sidecar, and global write guarantees.
Phase 1 defines schemas only; it provides no commands that write proposals or
decisions, and no learning command can modify the target repository or global
tool checkout.

## Consequences

Operators can inspect the foundation safely before opting in. Target-specific
approval and retention choices stay reviewable in the target policy, while
potentially sensitive artifacts remain local to the target's sidecar.

Future phases must add a new ADR or amend this one before broadening writes,
changing ownership, adding a default preset, or allowing a learning record to
trigger a target/global action.
