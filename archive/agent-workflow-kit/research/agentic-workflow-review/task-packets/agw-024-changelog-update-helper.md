# AGW-024 Task Packet: Changelog Update Helper

## Task

- ID: AGW-024
- Priority: P2
- Repo: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- Status: approved
- Source: `research/agentic-workflow-review/backlog.csv:25`

Add a deterministic local changelog-update helper tied to docs-impact results.
It should propose/check release-note work by default, not mutate target release
files by default.

## Safe Start Evidence

- Source main is clean and pushed at `6417391e36f1c485f6f90c152754c0abe2fc738c`.
- Kit main is clean and pushed at `3fdbbcd1efc211c1d4635e64d039910379c213a1`.
- `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
  in the source repo reported zero active tasks, hazards, stale tasks, unknown
  scopes, and untracked task worktrees.
- `make agent-next` selects AGW-024 with a clean source checkout.

Decision: safe-start.

## Implementation Scope

Allowed kit areas include changelog helper implementation, wrapper CLI, installed
Make target, versioning/docs-impact docs, tests, `VERSION`, and `CHANGELOG.md`.
Source closeout is limited to backlog, repo split backlog, summary, and feature
matrix after kit validation passes.

## Acceptance

1. A local changelog-update helper produces deterministic JSON/text proposals
   from docs-impact or changed-file input without writing by default.
2. Output reports target `VERSION`/`CHANGELOG.md` state, changelog need,
   candidate changelog text, docs-impact categories, and next safe commands.
3. Wrapper CLI and installed Make target expose the helper.
4. Docs and slash-command grammar explain the local helper and keep write
   behavior behind explicit accepted scope.
5. VERSION and CHANGELOG record the repo-contract-kit behavior change.
6. Source backlog rows and summary close AGW-024 only after kit validation.

## Required Validation

Run in repo-contract-kit:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_changelog_update tests.test_repo_contract_kit_cli tests.test_install tests.test_versioning`
- `PYTHONDONTWRITEBYTECODE=1 make test`
- `make docs-check`
- `make version-check`
- `git diff --check`

Run in the source repo after closeout:

- `make backlog-check`
- `make backlog-split-check`
- `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
- `git diff --check`

## Non-Goals

- Do not create an autonomous release bot or open PRs.
- Do not write `CHANGELOG.md` or `VERSION` by default.
- Do not change SemVer bump semantics or release tagging.
- Do not replace docs-impact, docs-propose, version-check, or version-bump.
