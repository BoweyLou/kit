# AGW-100 Task Packet: Public Repo-Contract-Kit Surface

## Task

- ID: `AGW-100`
- Title: Consolidate the workflow stack into one public repo-contract-kit product surface.
- Priority: `P0`
- Status: `draft`
- Source: `research/agentic-workflow-review/backlog.csv:101`

## Context

- Repository: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Source/control repository: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Mode: `implementation`
- Problem statement: Target-repo operators should not need to understand a
  two-repo workflow stack. The normal surface should be the public
  `repo-contract-kit` installer and `kit` commands, while legacy
  `agent-workflow-kit` / `Codex_CodeReview` source context remains readable as
  migration/archive evidence.
- Current evidence:
  - `make backlog-status` selects `AGW-100` as the next open item.
  - The source checkout is dirty with dogfood `repo-contract-kit 0.5.0`
    migration files and an unrelated draft `AGW-101` story packet.
  - Dummy migration testing from `0.4.41` to the current `0.5.0` source
    succeeded for clean and customized targets, but surfaced observability and
    instruction-budget follow-up issues.

## Previous Task State

- Active local tasks: none reported by `make agent-task-status`.
- Dirty state to preserve:
  - Dogfood `0.5.0` kit migration in this source repo.
  - Draft `AGW-101` backlog row and packet files.
- Closeout required before implementation:
  - Commit this packet separately.
  - Keep subsequent `AGW-100` implementation and closeout commits separate from
    the `AGW-101` packet/story work.

## Scope

Inspect first:

- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/README.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/install.sh`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/repo_contract_kit.py`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/update.py`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/common/AGENTS.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/common/working-rhythm.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/tests/test_repo_contract_kit_cli.py`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/tests/test_update.py`

Allowed edits:

- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/README.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/install.sh`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/common/`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/tests/`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/VERSION`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/CHANGELOG.md`
- Source closeout files under `research/agentic-workflow-review/` after kit
  validation passes.

Protected:

- Do not move target-repo `AGENTS.md` out of the root in this task.
- Do not make target operators use the legacy workflow-source checkout.
- Do not hide update conflicts or overwrite customized target files.
- Do not mix `AGW-101` implementation into `AGW-100`.

## Acceptance Criteria

- Public docs and installer guidance make `repo-contract-kit` / `kit` the only
  normal target-repo entrypoint.
- `kit self status/update`, `kit target add/status/update/doctor`, and
  `kit update` behavior are documented without requiring a workflow-source
  checkout.
- Dogfood install in `Codex_CodeReview` reports `repo-contract-kit 0.5.0`,
  current prompt snapshot, and sidecar availability.
- Migration from an older target install to the current kit is covered by a
  clean-target and customized-target test or documented receipt.
- `kit update --json --apply` reports enough structured action/conflict/write
  evidence for automation to diagnose migrations.
- Root `AGENTS.md` remains a short route map and passes the installed
  instruction budget.
- `AGW-100` backlog rows and summary are marked done only after repo-contract-kit
  validation and source dogfood checks pass.

## Validation

Run in `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_repo_contract_kit_cli tests.test_update tests.test_install`
- `PYTHONDONTWRITEBYTECODE=1 make test`
- `make docs-check`
- `make version-check`
- `git diff --check`

Run in `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview` after source closeout:

- `make kit-status KIT=/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- `make stack-status KIT=/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- `make backlog-status`
- `make backlog-check`
- `make agent-next`
- `make agent-verify`
- `git diff --check`
