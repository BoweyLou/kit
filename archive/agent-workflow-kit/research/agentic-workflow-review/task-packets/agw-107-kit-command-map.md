# AGW-107 Task Packet: Kit Command Map

## Source

- Backlog item: `AGW-107`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Source repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`

## Problem

Agents and humans can inspect individual `kit` commands, but there is no
schema-versioned command discovery surface that explains the command tree,
supported JSON modes, mutation behavior, sidecar writes, examples, output
contracts, and aliases in one place.

## Scope

- Add `kit command-map --json`.
- Add `kit agent-context --json` as an alias surface for agent bootstrap.
- Generate the command list from argparse parser metadata and decorate it with
  explicit static annotations for audience, mutation class, examples, aliases,
  and output schema pointers.
- Include parser consistency metadata so drift between the command map and real
  parser tree is visible.
- Keep the command non-mutating and independent of a target git repository.
- Update human docs and release metadata.

## Non-Goals

- Do not redesign command names or existing JSON payloads.
- Do not add network calls, hosted model calls, or target-repo writes.
- Do not solve the later natural-language or progressive-disclosure backlog
  items in this task.

## Acceptance

- `kit command-map --json` exits `0` outside a git repository.
- The payload has `schema_version: 1`, `command: "command-map"`, no target
  writes, no sidecar writes, and a deterministic sidecar state block.
- The payload includes entries for `status`, `update`, `target update`,
  `task-packet`, `agent-context-bundle`, and `command-map`.
- Command entries include flags, audience, mutation class, sidecar write
  behavior, JSON support, aliases, examples, exit code notes, output schema
  pointers, and doc pointers.
- `kit agent-context --json` returns the same command catalogue with
  `alias_of: "command-map"`.
- `kit help --all` and README documentation mention the discovery surface.

## Validation

- Add a failing unit test first for the JSON payload and alias.
- Run the focused CLI test before implementation to confirm the expected red
  state.
- After implementation, run focused tests, `make test`, `make docs-check`,
  `make docs-freshness`, `make version-check`, and `git diff --check`.
