# AGW-021 Task Packet: Config Migration

## Task

- ID: AGW-021
- Priority: P2
- Repo: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- Status: approved
- Source: `research/agentic-workflow-review/backlog.csv:22`

Add a plan-first config/profile migration path for repo-contract-kit installs
when profile or install metadata schema changes.

## Safe Start Evidence

- Source main is clean and pushed at `b1c4680fc2f92279f948d820f8e1965cfc7c662e`.
- Kit main is clean and pushed at `2b3ef0bda8fff66fc4c7cfc334b99b39fe23578a`.
- `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
  in the source repo reported zero active tasks, hazards, stale tasks, unknown
  scopes, and untracked task worktrees.
- `make agent-next` selects AGW-021 with a clean source checkout.

Decision: safe-start.

## Implementation Scope

Allowed kit areas:

- `scripts/update.py`
- `scripts/install.py`
- `scripts/repo_contract_kit.py`
- `templates/common/kit-makefile.mk`
- `templates/common/working-rhythm.md`
- `templates/common/ops-agent-workflow.md`
- `docs/rollout-guide.md`
- `docs/adr/0002-managed-updates-and-versioning.md`
- `README.md`
- `CHANGELOG.md`
- `VERSION`
- `tests/test_update.py`
- `tests/test_repo_contract_kit_cli.py`
- `tests/test_install.py`

Source closeout files are limited to the backlog, repo split backlog, summary,
and feature matrix after kit validation passes.

## Acceptance

1. New install/update metadata carries a deterministic current profile/config
   migration marker or equivalent schema marker.
2. `update-plan` detects missing or outdated profile/config schema metadata and
   reports migration actions without writing target repo files.
3. Explicit apply migrates only kit metadata needed for schema drift and still
   preserves target-owned files and customized managed-file conflicts.
4. Wrapper CLI and docs expose the migration/update path while keeping
   `update-plan` non-mutating.
5. VERSION and CHANGELOG record the repo-contract-kit behavior change.
6. Source backlog rows and summary close AGW-021 only after kit validation.

## Required Validation

Run in repo-contract-kit:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_update tests.test_repo_contract_kit_cli tests.test_install`
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

- Do not rewrite update/install architecture.
- Do not make plan commands mutate target repos.
- Do not migrate arbitrary target-owned files or user customizations.
- Do not add hosted CI, GitHub-only, or PR-bot behavior.
- Do not change agent-workflow-kit prompts or schemas for this item.
