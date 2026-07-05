# ADR 0004: Batch Maintenance App Write Exceptions

## Status

Accepted

## Context

ADR 0003 allowed Kit Companion to run one confirmed write workflow for dirty
repo closeout while keeping the generic command browser read-only or
preview-only.

Operators also need to clean multiple repos from the app without opening a
terminal for every low-risk maintenance step. The CLI already has constrained
write commands for target registry import, stale missing-target pruning, clean
target updates, and clean disposable worktree pruning. These commands have
preview forms, JSON output, and existing CLI gates that avoid dirty target
rewrites or dirty worktree deletion.

## Decision

Keep the generic Kit Companion command browser read-only or preview-only.
Add dedicated Batch tab write actions for these exact command shapes:

- `kit target import --root <selected-target> --apply --json`
- `kit target prune-missing --apply --json`
- `kit worktree prune --root <selected-target> --apply --json`
- `kit target update-all --apply --json`
- `kit target closeout-all --apply --policy gated --json`

Add batch guided closeout for dirty target repos by queueing separate
`kit closeout-fix --repo <target> --apply --jsonl` jobs with a concurrency
limit of two. The app must keep per-repo job cards, events, result payloads,
receipts, and blockers separate.

Use `target closeout-all` for all-registry overnight closeout automation. It
must read registered targets only, use the gated closeout policy, and report
`CLEAN`, `CLEANED`, `LEFT-UNFINISHED`, `NEEDS-REVIEW`, or `FAILED` without
normalizing ambiguous work.

Do not allow the app write runner to execute setup, install, global tool
updates, self updates, custom closeout agents, arbitrary target writes,
`--force`, or `--write-sidecar` commands.

## Consequences

Kit Companion becomes useful for multi-repo cleanup while preserving the CLI as
the source of truth. App-side writes remain explicit, confirmed, and narrow.

The Batch tab now needs to explain which writes are app-safe and which remain
Terminal handoffs. Future write expansion should add a new allowlist entry,
confirmation copy, tests, and documentation rather than relaxing the generic
command browser.
