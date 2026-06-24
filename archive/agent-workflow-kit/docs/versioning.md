# Versioning

agent-workflow-kit uses local SemVer in `VERSION` as the source of truth.
`CHANGELOG.md` records the release notes for each version.

## Commands

- `make version-status` prints the current version.
- `make version-check` validates that `VERSION` uses SemVer, including optional
  prerelease labels such as `0.2.0-beta.1`, and confirms `CHANGELOG.md` has an
  entry for that version.
- `make version-bump BUMP=patch` updates `VERSION` and prepends a changelog
  stub. `BUMP=minor` and `BUMP=major` are also supported.
- `make version-commit-check` runs the staged commit gate directly.
- `make install-git-hooks` configures this checkout to run `.githooks/pre-commit`
  on every commit.

## Commit Gate

The pre-commit gate always validates the version baseline. It also requires both
`VERSION` and `CHANGELOG.md` to be staged when a commit changes version-impacting
surfaces:

- `.codex/prompts/`
- `.github/copilot-instructions.md`
- `workflows/`
- `schemas/`
- `scripts/`
- `research/agentic-workflow-review/backlog.csv`
- `research/agentic-workflow-review/agent-workflow-kit-backlog.csv`
- `research/agentic-workflow-review/repo-contract-kit-backlog.csv`
- `examples/`
- `.githooks/`
- `Makefile`
- `.pre-commit-config.yaml`

Research and planning docs do not require a version bump by default. For an
intentional no-version-change commit that touches an impacting path, run the
commit with `VERSION_CHECK_ALLOW_UNCHANGED=1`.
