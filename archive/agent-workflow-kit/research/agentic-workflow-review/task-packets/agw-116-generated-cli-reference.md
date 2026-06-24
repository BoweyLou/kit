# AGW-116 Task Packet: Generated CLI Reference

## Source

- Backlog item: `AGW-116`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Source repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`

## Problem

The command map is now the structured CLI source of truth, but human CLI
reference docs can still drift if they are hand-maintained. The repo needs a
generated reference surface and a freshness check that fails when command
metadata changes without refreshing docs.

## Scope

- Add `kit cli-reference`.
- Generate Markdown and JSON from `kit command-map --json` metadata.
- Commit a generated `docs/cli-reference.md`.
- Include generated Markdown docs-as-tests claim metadata in JSON output.
- Add `--check` to compare generated Markdown with a reference file.
- Add `--write` to refresh the generated reference file.
- Wire `make docs-freshness` to fail when `docs/cli-reference.md` drifts.
- Document the new command and update release metadata.

## Non-Goals

- Do not replace the existing experimental OpenAPI/JSON docs-as-tests profile.
- Do not generate the full README from command metadata.
- Do not add hosted docs publishing.
- Do not add a new external documentation generator dependency.

## Acceptance

- `kit cli-reference` prints generated Markdown containing command sections,
  flags, examples, mutation class, target-write behavior, and schema metadata.
- `kit cli-reference --json` emits command-map-derived metadata and
  docs-as-tests claim objects for Markdown section coverage.
- `kit cli-reference --check docs/cli-reference.md` passes when the committed
  file is current and fails on stale content.
- `make docs-freshness` runs the CLI-reference drift check.
- Regression tests cover command-map metadata, Markdown/JSON generation, and
  stale-doc failure.

## Validation

- Add failing CLI-reference tests before implementation.
- After implementation, run focused CLI-reference tests, `make test`,
  `make docs-check`, `make docs-freshness`, `make version-check`,
  `make workflow-source-check`, and `git diff --check` in `repo-contract-kit`.
- After pushing implementation, close AGW-116 in the source backlog and run
  source `make backlog-check`, `make backlog-split-check`, `make agent-verify`,
  and `git diff --check`.
