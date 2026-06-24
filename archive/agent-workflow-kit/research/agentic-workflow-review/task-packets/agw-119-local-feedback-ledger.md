# AGW-119 Task Packet: Local Feedback Ledger

## Source

- Backlog item: `AGW-119`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Source repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`

## Problem

Humans and agents can hit confusing `kit` recovery paths repeatedly, but there
was no durable local place to capture that friction. Sending upstream issues or
network telemetry would be too noisy and too broad; the right default is a
repo-scoped local ledger with explicit privacy metadata.

## Scope

- Add `kit feedback`.
- Append feedback entries to a repo sidecar JSONL ledger.
- Include timestamp, repo id, tool version, target version, source, message,
  context command, optional last error, and tags.
- Support read-only `--list`, `--export-json`, and `--limit` modes.
- Keep feedback storage local: no network calls, no issue creation, no upstream
  submission, and no target-repo writes.
- Add feedback sidecar path metadata and command-map metadata.
- Update README, generated CLI reference, changelog, version, and tests.

## Non-Goals

- Do not submit feedback to GitHub, issue trackers, or hosted services.
- Do not write feedback into the target repository.
- Do not make feedback capture automatic on every error.
- Do not add analytics or telemetry.

## Acceptance

- Recording feedback appends one JSONL entry under the repo sidecar and reports
  sidecar writes only.
- Export/list modes read the ledger without creating sidecar state.
- Empty export returns an empty entry list and does not create sidecar state.
- Payloads include privacy metadata proving no network or upstream submission.
- Generated CLI reference and command-map metadata include `kit feedback`.

## Implementation

- repo-contract-kit `0.6.18`
- Commit: `1ac264a Add kit feedback ledger`
- Main files:
  - `scripts/repo_contract_kit.py`
  - `tests/test_repo_contract_kit_cli.py`
  - `docs/cli-reference.md`
  - `README.md`
  - `CHANGELOG.md`
  - `VERSION`

## Validation

- Red-first focused tests initially failed because `feedback` was not a known
  command.
- Focused feedback tests passed for add, export, empty export, sidecar path, and
  version metadata behavior.
- `make docs-check` passed.
- `make docs-freshness` passed and confirmed `docs/cli-reference.md` is
  current.
- `make version-check` passed for `0.6.18`.
- `make workflow-source-check` passed.
- `git diff --check` passed.
- `make test` passed: 286 tests.
