# AGW-121 Task Packet: Kit Drift Diagnostics

## Source

- Backlog item: `AGW-121`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Source repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`

## Problem

Operators can see two true but confusing states at once: the running global
`kit` tool can be newer than the target repo install receipt. The CLI should
explain whether that state is acceptable, stale, newer-target, unknown, or
not-installed, and it should point to safe repair commands without applying
updates automatically.

## Scope

- Add structured `kit_drift` diagnostics to `kit status --json`.
- Add the same diagnostic to `kit doctor`, `kit agent-preflight`,
  `kit agent-doctor`, and target aliases.
- Compare running global tool/local kit version, source ref, and prompt snapshot
  against the target install receipt.
- Classify drift as `acceptable`, `stale`, `newer-target`, `unknown`, or
  `not-installed`.
- Print safe next commands such as `kit update --dry-run --repo ...`,
  `kit update --repo ...`, `kit update --global`, and `kit self update`.
- Publish `kit_drift` as a stable command-map JSON contract field.
- Update README, changelog, version metadata, and tests.

## Non-Goals

- Do not automatically update the global tool or target install.
- Do not turn stale drift into a hard doctor blocker.
- Do not change target files or sidecar state during diagnostics.
- Do not replace the existing update-plan or update dry-run flows.

## Acceptance

- `status --json` returns `kit_drift` with classification, reason, compared
  refs/snapshots, no-write metadata, and next commands.
- `doctor --json` includes `kit_drift` and non-blocking warning details for
  stale, newer-target, or unknown drift.
- Text `status` and `doctor` outputs surface the classification and safe next
  commands.
- Command-map JSON contracts advertise `kit_drift` for status and doctor
  payloads.

## Implementation

- repo-contract-kit `0.6.20`
- Commit: `0986d6c Add kit drift diagnostics`
- Main files:
  - `scripts/repo_contract_kit.py`
  - `tests/test_repo_contract_kit_cli.py`
  - `README.md`
  - `CHANGELOG.md`
  - `VERSION`

## Validation

- Red-first focused tests initially failed because `kit_drift` was absent from
  status and doctor payloads.
- Focused AGW-121 tests passed for stale target install, newer target install,
  status text guidance, doctor warning details, and command-map stable fields.
- `make cli-ux-fixtures` passed.
- `make docs-check` passed.
- `make docs-freshness` passed and confirmed `docs/cli-reference.md` is
  current.
- `make version-check` passed for `0.6.20`.
- `make workflow-source-check` passed.
- `git diff --check` passed.
- `make test` passed: 294 tests.
