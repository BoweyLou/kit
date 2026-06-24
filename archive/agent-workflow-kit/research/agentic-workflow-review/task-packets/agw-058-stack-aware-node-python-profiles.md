# AGW-058 Task Packet: Stack-Aware Node And Python Profiles

## Task

- ID: `AGW-058`
- Title: Implement stack-aware Node and Python template profiles.
- Priority: `P2`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv:59`
- Repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`

## Context

Placeholder Node and Python stack profiles should become useful opt-in defaults
for common target repos without installing dependencies or taking over
application scaffolding.

Safe-start evidence:

- `make backlog-status` reports `3` open, `98` done, `0` partial, with
  `AGW-058` selected next.
- `make agent-next` selects `AGW-058` and reports `dirty: false`.
- `make agent-task-status` reports zero active tasks and no coordination
  warnings.
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit` is clean at `be27b2f`.
- Prior AGW-055 work is committed in Codex_CodeReview as `6d21797`.

Non-goals:

- Do not install npm, pnpm, yarn, pip, uv, poetry, tox, pytest, or any project
  dependencies.
- Do not generate application source trees, lockfiles, virtual environments, or
  framework-specific CI.
- Do not make Node or Python profiles part of every install unless an existing
  preset already explicitly selects them.
- Do not edit Codex_CodeReview prompt sources for this repo-contract-kit task.

## Goal Alignment

- Repo goal: `repo-contract-kit` installs safe docs-as-code and agent workflow
  scaffolding into target repos while preserving target-owned work.
- Aligned areas:
  - `templates/profiles/node/` for opt-in Node-oriented profile files.
  - `templates/profiles/python/` for opt-in Python-oriented profile files.
  - `scripts/install.py`, `scripts/update.py`, and tests for profile mechanics.
  - `README.md`, `docs/rollout-guide.md`, and changelog/version files for
    user-visible profile behavior.
- Decision: `aligned`.
- Stop if the work requires package installation, framework detection, generated
  app code, or unsafe target-owned file overwrites.

## Scope

Inspect first:

- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/AGENTS.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/README.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/docs/rollout-guide.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/profiles/`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/install.py`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/update.py`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/tests/test_install.py`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/tests/test_update.py`

Allowed edits:

- `templates/profiles/node/**`
- `templates/profiles/python/**`
- `scripts/install.py`
- `scripts/update.py`
- `tests/test_install.py`
- `tests/test_update.py`
- `README.md`
- `docs/rollout-guide.md`
- relevant common template docs if profile guidance belongs there
- `VERSION`
- `CHANGELOG.md`
- Codex_CodeReview dogfood and backlog closeout files after validation

Protected:

- Runtime credentials, package manager caches, `node_modules`, virtual
  environments, lockfiles, and dependency installation.
- Application source files in dummy or target repos outside managed templates.
- Codex_CodeReview canonical workflow prompt sources.
- Existing target-owned files except through reviewed update proposal artifacts.

## Acceptance Criteria

- Node and Python profiles install useful stack-aware defaults instead of
  placeholders.
- Profiles remain opt-in and do not install dependencies, generate lockfiles, or
  assume a framework.
- Update safety is preserved for managed files and target-owned customizations.
- Operator docs describe profile selection and boundaries.
- Codex_CodeReview dogfood install reflects the new kit version/source ref after
  repo-contract-kit validation.

## Validation

Run from `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install tests.test_update`
- `PYTHONDONTWRITEBYTECODE=1 make test`
- `make docs-check`
- `make version-check`
- `git diff --check`

Run from `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview` after dogfood update:

- `make kit-update KIT=/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- `make backlog-check && make backlog-split-check && make backlog-status && make agent-next`
- `make kit-status KIT=/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- `make docs-check && make version-check && git diff --check`

Capture evidence:

- Profile template file list before and after implementation.
- Focused install/update and full test output.
- Dummy install evidence for `--profile node` and `--profile python`.
- Dogfood `kit-status` output.
- Backlog closeout status and next open item.

## Closeout Requirements

- Final receipt path: `.agent-workflows/tasks/AGW-058/receipt.json` or sidecar
  equivalent, or explain why unavailable.
- Readiness: `make agent-task-ready TASK=AGW-058 TASK_READY_JSON=1` or record
  why unavailable.
- Lifecycle: `make agent-task-finalize TASK=AGW-058
  TASK_RECEIPT=.agent-workflows/tasks/AGW-058/receipt.json TASK_FINALIZE_JSON=1`
  or durable fallback receipt.
- Final task status: `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1
  TASK_STATUS_JSON=1`.
- Closeout preview: `make agent-task-closeout TASK_CLOSEOUT_JSON=1`; apply
  requires explicit approval.
- Final handoff must classify remaining dirty files in both repos.

## Documentation Impact

Expected: yes.

Required docs/update paths:

- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/README.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/docs/rollout-guide.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/CHANGELOG.md`
- `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-workflow-review/summary.md`
- `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/CHANGELOG.md`

No docs waiver is allowed because profile behavior is user-visible install
behavior.

## Risk And Approval

Risk level: medium.

Known risks:

- Stack profiles could overreach into framework scaffolding or dependency
  management.
- New profile files could be added without managed manifest coverage.
- Docs could imply package-manager behavior the kit deliberately does not
  perform.
- Dogfood update could preserve local managed-file conflicts that need review
  rather than force-overwrite.

Approval: approved by the user's serial backlog execution request.

Recommended prompt: `workflows/prompts/fix-implementer.md`.

Next packet hint: keep external planning and memory adapter examples separate
for `AGW-059`.
