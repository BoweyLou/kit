# AGW-112 Task Packet: Command Route Taxonomy

## Source

- Backlog item: `AGW-112`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Source repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`

## Problem

`kit setup`, `kit target add`, `kit install`, `kit doctor`,
`kit target doctor`, `kit agent-doctor`, and `kit agent-preflight` all work, but
their relationships are implicit. Humans and agents need the command map to say
which route is canonical, which route is an alias, which route is agent-only,
which route is maintainer-oriented, and which routes exist for compatibility.

## Scope

- Add route taxonomy fields to `kit command-map --json` and
  `kit agent-context --json`.
- Mark canonical, alias, agent-only, maintainer, namespace, and compatibility
  routes.
- Add canonical command pointers, alias groups, and route notes for ambiguous
  setup/install/target and doctor/preflight surfaces.
- Preserve existing command behavior and JSON fields.
- Document the command-map route taxonomy.

## Non-Goals

- Do not remove or deprecate working aliases.
- Do not change setup/install/update mutation behavior.
- Do not add completions or generated docs in this slice.

## Acceptance

- `kit command-map --json` includes `route_role`, `canonical_command`,
  `alias_group`, and `route_note` fields for commands.
- `setup` is marked as the canonical target-enrollment route.
- `target add` is marked as the explicit namespace alias for `setup`.
- `install` is marked as the agent/source explicit install route with
  `setup` as the canonical command.
- `doctor` is marked as canonical diagnostics, while `target doctor`,
  `agent-doctor`, and `agent-preflight` point back to it.
- `self update` is marked as maintainer/global-tool work.
- `migrate-config` is marked as a compatibility route for metadata-only update.
- README and changelog explain the additive command-map metadata.

## Validation

- Add failing command-map tests before implementation.
- After implementation, run focused command-map tests, `make test`,
  `make docs-check`, `make docs-freshness`, `make version-check`,
  `make workflow-source-check`, and `git diff --check` in `repo-contract-kit`.
- After pushing implementation, close AGW-112 in the source backlog and run
  source `make backlog-check`, `make backlog-split-check`, and
  `make agent-verify`.
