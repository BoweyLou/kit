# AGW-115 Task Packet: TTY Command Palette

## Source

- Backlog item: `AGW-115`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Source repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`

## Problem

Humans need an ergonomic way to search the `kit` command surface, inspect exact
commands, and see mutation/write behavior without turning interactivity into the
default path for agents or scripts. The palette must stay optional, TTY-only,
and dependency-light.

## Scope

- Add a read-only `kit palette` command.
- Search command names, summaries, examples, and mutation classes from the
  parser-backed command map.
- Add `--query` for an initial search term.
- Add `--print-command` for exact command preview without entering the chooser.
- Show mutation class, target-write behavior, and sidecar-write behavior.
- Disable the palette under non-TTY sessions, `--no-input`, and `KIT_AGENT=1`.
- Require explicit `yes` confirmation before printing mutating commands.
- Document the palette behavior in README and release metadata.

## Non-Goals

- Do not run selected commands.
- Do not add prompt_toolkit, Gum, Trogon, or other interactive dependencies.
- Do not enable the palette for agents or non-TTY scripts.
- Do not implement generated CLI reference docs in this slice.

## Acceptance

- `kit palette` is advertised in `kit command-map --json` as a read-only,
  human-facing, text-only route.
- `kit palette --query status --print-command` prints the exact matching command
  and write-behavior metadata when run in a TTY.
- Non-TTY, `--no-input`, and `KIT_AGENT=1` runs do not prompt and instead point
  callers to `kit command-map --json` and `kit options`.
- Interactive mutating selections require `yes` before printing the command.
- Regression tests cover disabled mode, exact command preview, mutating
  confirmation, and command-map metadata.

## Validation

- Add failing palette tests before implementation.
- After implementation, run focused palette tests, `make test`,
  `make docs-check`, `make docs-freshness`, `make version-check`,
  `make workflow-source-check`, and `git diff --check` in `repo-contract-kit`.
- After pushing implementation, close AGW-115 in the source backlog and run
  source `make backlog-check`, `make backlog-split-check`, `make agent-verify`,
  and `git diff --check`.
