# AGW-120 Task Packet: Agent Tool Manifest

## Source

- Backlog item: `AGW-120`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Source repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`

## Problem

Agents need to consume the same command contract that humans, completions, and
generated docs use. Without a compact manifest, downstream local agents or tool
adapters have to scrape help text or copy stale command rules.

## Scope

- Add `kit agent-tool-manifest --json`.
- Derive the manifest from `kit command-map --json`.
- Separate read-only safe commands, target-writing commands, sidecar-writing
  commands, schemas, examples, and no-input behavior.
- Include an explicit local integration contract: no network calls, no hosted
  model calls, no credentials, no target-repo writes, and no sidecar writes.
- Add command-map metadata, README docs, generated CLI reference docs,
  changelog, version metadata, and tests.

## Non-Goals

- Do not add MCP hosting, hosted model calls, credentials, or network behavior.
- Do not make the manifest a second hand-maintained command catalogue.
- Do not write target repo files or sidecar state.
- Do not replace the full `command-map --json` catalogue.

## Acceptance

- `command-map --json` lists `agent-tool-manifest` as an agent-only read-only
  route with no target or sidecar writes.
- `agent-tool-manifest --json` returns safe command groups, write-command
  groups, schemas, examples, parser consistency status, no-input metadata, and
  no-network/no-credential integration metadata.
- Text output points operators to the JSON contract.
- Generated CLI reference and docs freshness checks include the command.

## Implementation

- repo-contract-kit `0.6.19`
- Commit: `351a6a7 Add kit agent tool manifest`
- Main files:
  - `scripts/repo_contract_kit.py`
  - `tests/test_repo_contract_kit_cli.py`
  - `docs/cli-reference.md`
  - `README.md`
  - `CHANGELOG.md`
  - `VERSION`

## Validation

- Red-first focused tests initially failed because `agent-tool-manifest` was
  not a known command.
- Focused AGW-120 tests passed for command-map metadata, JSON manifest payload,
  and text output.
- `make docs-check` passed.
- `make docs-freshness` passed and confirmed `docs/cli-reference.md` is
  current.
- `make version-check` passed for `0.6.19`.
- `make workflow-source-check` passed.
- `git diff --check` passed.
- `make test` passed: 289 tests.
