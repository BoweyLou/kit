# AGW-118 Task Packet: Optional Human Summary Styling

## Source

- Backlog item: `AGW-118`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Source repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`

## Problem

The compact `kit doctor` and `kit update` summaries are readable in plain text,
but interactive operators benefit from restrained visual emphasis. Styling must
remain optional: pipes, captures, JSON, and `NO_COLOR` users need the same plain
contract and no semantic dependence on color.

## Scope

- Add stdlib-only human summary styling for selected doctor/preflight and update
  summary renderers.
- Add `--style auto|plain|pretty` on the summary-producing command surfaces.
- Preserve plain default behavior for non-TTY output and `--style plain`.
- Respect `NO_COLOR` even when `--style pretty` is requested.
- Keep JSON output free of ANSI styling.
- Publish style metadata in the command-map CLI metadata and refresh generated
  CLI reference docs.
- Update README, changelog, version metadata, and regression fixtures.

## Non-Goals

- Do not add Rich, prompt_toolkit, or another runtime dependency.
- Do not replace line-oriented summaries with tables that scripts might parse.
- Do not make color carry meaning that is absent from text.
- Do not style JSON, shell completions, generated Markdown, or command-map data.

## Acceptance

- Pretty style adds ANSI emphasis to human doctor/update summaries when
  explicitly requested and `NO_COLOR` is not set.
- `NO_COLOR=1` suppresses ANSI output even with `--style pretty`.
- JSON output remains valid JSON and contains no ANSI escapes.
- Default captured output stays plain.
- `docs/cli-reference.md` includes the new style flags and `make
  docs-freshness` passes.

## Implementation

- repo-contract-kit `0.6.17`
- Commit: `f5ccdfe Add optional kit summary styling`
- Main files:
  - `scripts/repo_contract_kit.py`
  - `tests/test_repo_contract_kit_cli.py`
  - `tests/fixtures/cli_ux/manifest.json`
  - `docs/cli-reference.md`
  - `README.md`
  - `CHANGELOG.md`
  - `VERSION`

## Validation

- Red-first focused tests initially failed because `--style` was not parsed.
- Focused style tests passed for pretty doctor output, `NO_COLOR`, JSON output,
  and pretty update output.
- `make cli-ux-fixtures` passed.
- `make docs-check` passed.
- `make docs-freshness` passed and confirmed `docs/cli-reference.md` is
  current.
- `make version-check` passed for `0.6.17`.
- `make workflow-source-check` passed.
- `git diff --check` passed.
- `make test` passed: 283 tests.
