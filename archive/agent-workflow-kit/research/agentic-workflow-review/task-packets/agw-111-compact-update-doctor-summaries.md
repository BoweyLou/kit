# AGW-111 Task Packet: Compact Update And Doctor Summaries

## Source

- Backlog item: `AGW-111`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Source repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`

## Problem

`kit update --dry-run`, `kit update`, and `kit doctor` already expose the right
machine-readable data, but the default human output is too verbose or starts at
the wrong level. Operators need the first screen to answer what is blocked, what
would change, where proposals were written, whether target or sidecar writes
happened, and what command should be run next.

## Scope

- Render human `kit update --dry-run` from the update plan instead of dumping
  plan JSON.
- Lead human `kit update` output with counts for blockers, conflicts, direct
  updates, target-owned files, proposal paths, and target/sidecar writes.
- Add a detail mode for update commands when the raw script output is still
  useful.
- Lead human `kit doctor` / `kit target doctor` output with blocker and count
  summaries before detailed dirty/task/worktree sections.
- Preserve existing JSON output exactly for agent consumers.
- Document the compact summary contract and update release notes.

## Non-Goals

- Do not change update mutation semantics.
- Do not change `scripts/update.py` JSON schemas.
- Do not add a TUI or interactive command palette.
- Do not hide conflicts or proposal paths from detailed output.

## Acceptance

- `kit update --dry-run` human output starts with a compact update summary, not
  raw JSON.
- Clean update and conflict update cases report blockers, conflicts, direct
  updates, target-owned counts, proposal paths, target writes, sidecar writes,
  and next commands.
- `kit update --verbose` and `kit target update --verbose` can show the raw
  script detail after the compact summary.
- `kit doctor` human output starts with a compact doctor summary and still lists
  detailed blockers, warnings, and recommendations.
- `kit update --json`, `kit update --dry-run --json`, and `kit doctor --json`
  remain machine-readable and compatible.

## Validation

- Add failing CLI tests first for human dry-run, clean apply, conflict apply,
  verbose detail, and doctor lead-in behavior.
- After implementation, run focused tests, `make test`, `make docs-check`,
  `make docs-freshness`, `make version-check`, `make workflow-source-check`, and
  `git diff --check` in `repo-contract-kit`.
- After pushing implementation, close AGW-111 in the source backlog and run
  source `make backlog-check`, `make backlog-split-check`, and `make agent-verify`.
