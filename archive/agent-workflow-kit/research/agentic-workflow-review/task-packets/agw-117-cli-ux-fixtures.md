# AGW-117 Task Packet: CLI UX Regression Fixtures

## Source

- Backlog item: `AGW-117`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Source repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`

## Problem

`kit` now has structured command metadata, actionable errors, non-interactive
mode, compact human summaries, completions, a command palette, and generated CLI
reference docs. Without fixture-backed UX checks, those surfaces can regress in
small wording or structure changes that make the tool less usable for humans or
less parseable for agents.

## Scope

- Add a fixture-driven CLI UX regression runner.
- Cover top-level help lanes, unknown-command recovery text, `KIT_AGENT=1`
  parse-error JSON, `--no-input` guide behavior, command-map JSON, compact
  `doctor` and `update --dry-run` summaries, palette non-TTY fallback, and
  generated CLI-reference freshness.
- Use temporary git repositories for repo-shaped cases so tests do not depend
  on the live checkout being clean or installed.
- Add review guidance for intentional wording or structure changes.
- Wire a dedicated `make cli-ux-fixtures` target.
- Update README, changelog, and version metadata.

## Non-Goals

- Do not snapshot every byte of CLI output.
- Do not make color, rich rendering, or optional styling part of AGW-117.
- Do not add hosted telemetry, issue creation, or feedback submission.
- Do not depend on a global installed `kit` command.

## Acceptance

- `tests.test_cli_ux_fixtures` fails when the fixture manifest is missing or a
  declared UX contract is broken.
- The manifest keeps assertions behavior-focused and specific to actionable
  phrases, JSON fields, and write-safety promises.
- `make cli-ux-fixtures` runs the fixture suite.
- Review guidance explains how to handle intentional wording changes without
  weakening the UX contract.
- Release metadata records repo-contract-kit `0.6.16`.

## Implementation

- repo-contract-kit `0.6.16`
- Commit: `4629aa2 Add kit CLI UX fixtures`
- Main files:
  - `tests/test_cli_ux_fixtures.py`
  - `tests/fixtures/cli_ux/manifest.json`
  - `docs/cli-ux-regression-fixtures.md`
  - `Makefile`
  - `README.md`
  - `CHANGELOG.md`
  - `VERSION`

## Validation

- Red-first check: `python3 -m unittest tests.test_cli_ux_fixtures` failed on
  missing `tests/fixtures/cli_ux/manifest.json`.
- Focused implementation check: `python3 -m unittest tests.test_cli_ux_fixtures`
  passed.
- `make cli-ux-fixtures` passed.
- `make docs-check` passed.
- `make docs-freshness` passed and confirmed `docs/cli-reference.md` is
  current.
- `make version-check` passed for `0.6.16`.
- `make workflow-source-check` passed.
- `git diff --check` passed.
- `make test` passed: 279 tests.
