# AGW-113 Task Packet: JSON Schema Consistency

## Source

- Backlog item: `AGW-113`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Source repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`

## Problem

Most agent-facing `kit` commands already support `--json`, but agents still
have to infer whether a command exposes JSON, which payload fields are stable,
where schema promises are documented, and whether a command writes target or
sidecar state. Text-only help and namespace routes also need explicit reasons
instead of looking like missing coverage.

## Scope

- Inventory current command-map JSON coverage for agent-facing routes.
- Add per-command JSON contract metadata to `kit command-map --json` and the
  `kit agent-context --json` alias.
- Publish schema pointers, stable payload fields, command-map fields, and
  compatibility notes for JSON commands.
- Publish explicit non-JSON reasons for text-only and namespace commands.
- Preserve the top-level `schema_version` contract.
- Add read-only write metadata to `kit version --json` so its advertised stable
  fields are present.
- Document the JSON compatibility promise in README and update release
  metadata.

## Non-Goals

- Do not introduce standalone JSON schema files in this slice.
- Do not change command routing, mutation behavior, or existing JSON field
  meanings.
- Do not remove text-only help or namespace commands.
- Do not implement completions, generated CLI docs, or command-map consumers.

## Acceptance

- `kit command-map --json` includes a top-level `json_contract` block.
- Every command-map entry includes a `json_contract` block with `supported`,
  `output_schema`, `schema_pointer`, stable payload fields, command-map fields,
  compatibility text, and non-JSON reasons when applicable.
- JSON-supported commands point to `README.md#json-payload-contracts`.
- Text-only commands explain that machine-readable help metadata comes from
  `command-map --json`.
- Namespace commands explain that callers should inspect subcommands.
- `kit version --json` includes `target_repo_writes.performed=false` and
  `sidecar_writes.performed=false`.
- Regression tests cover stable field presence and write metadata.

## Validation

- Add failing command-map contract tests before implementation.
- After implementation, run focused command-map/version tests, `make test`,
  `make docs-check`, `make docs-freshness`, `make version-check`,
  `make workflow-source-check`, and `git diff --check` in `repo-contract-kit`.
- After pushing implementation, close AGW-113 in the source backlog and run
  source `make backlog-check`, `make backlog-split-check`, `make agent-verify`,
  and `git diff --check`.
