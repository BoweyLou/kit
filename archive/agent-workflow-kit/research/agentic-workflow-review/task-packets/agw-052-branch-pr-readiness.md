# AGW-052 Task Packet: Branch Or PR Readiness JSON

## Task

- ID: `AGW-052`
- Title: Create a branch-or-PR readiness JSON command that aggregates local
  evidence, CI/check inputs, docs-contract status, waiver state, and review
  disposition.
- Priority: `P2`
- Repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv:53`

`repo-contract-kit` has task-worktree readiness, finalizer, docs-impact,
changelog, receipt, and context-bundle surfaces, but no single branch-or-PR
readiness command that aggregates local evidence and optional hosted-CI/check
inputs before humans consider PR update, merge queue, auto-merge, or
branch-protection governance. Agents can still over-trust partial green checks
or loop across separate commands.

## Safe Start Evidence

- `agent-workflow-kit` source `main` is clean and ahead of origin with local
  packet/implementation/closeout commits through `3aa7deb`.
- `make backlog-status` in `agent-workflow-kit` reports `6` open and `95` done.
- `make agent-next` selects `AGW-052` with `dirty: false`.
- `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
  reports zero active tasks, no stale tasks, no hazards, no unknown-scope tasks,
  and no untracked agent worktrees.
- `repo-contract-kit` source `main` is clean and ahead of origin with local
  implementation commits through `10e7542`.
- `repo-contract-kit` `VERSION` is `0.6.0`.
- `repo-contract-kit` preflight passed:
  - `make test`
  - `make docs-check`
  - `make docs-freshness`
  - `make version-check`
  - `git diff --check`

Decision: `safe-start`.

## Implementation Scope

Allowed edits in `repo-contract-kit`:

- `scripts/repo_contract_kit.py`
- a new helper script if useful, such as `scripts/branch_readiness.py`,
  `scripts/pr_readiness.py`, or `scripts/agent_branch_readiness.py`
- `scripts/agent_task_ready.py` only for narrow shared helper extraction
- `templates/common/kit-makefile.mk`
- `templates/common/working-rhythm.md`
- `templates/common/ops-agent-workflow.md`
- `templates/common/harness-engineering.md`
- `docs/harness-engineering.md`
- `docs/rollout-guide.md`
- `README.md`
- focused tests, especially `tests/test_repo_contract_kit_cli.py`,
  `tests/test_install.py`, `tests/test_agent_task_ready.py`, or a new
  `tests/test_branch_readiness.py`
- `VERSION`
- `CHANGELOG.md`

Allowed source closeout edits in `agent-workflow-kit` after kit validation:

- `research/agentic-workflow-review/backlog.csv`
- `research/agentic-workflow-review/repo-contract-kit-backlog.csv`
- `research/agentic-workflow-review/summary.md`
- `research/agentic-workflow-review/feature_matrix.csv`

Protected:

- GitHub workflows or hosted branch-protection configuration, except
  documentation examples deferred to `AGW-053`.
- User target repositories outside the kit checkout.
- Credentials, tokens, API keys, local provider config, or CI secrets.
- Existing `agent-task-ready` per-task semantics except narrow shared helper
  extraction.
- Task lifecycle, closeout, automation-handoff, update-plan, and install
  behavior unrelated to readiness.
- Unrelated backlog rows.

## Inspect First

Read:

- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/repo_contract_kit.py`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/agent_task_ready.py`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/agent_task_finalize.py`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/check_doc_impact.py`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/changelog_update.py`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/agent_task_status.py`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/branch_readiness.py`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/common/kit-makefile.mk`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/common/working-rhythm.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/common/ops-agent-workflow.md`
- relevant tests under `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/tests/`

If using hosted-governance language, verify against current primary docs. At
packet creation, useful sources were GitHub protected branch docs, status check
docs, commit statuses REST docs, and merge queue docs. Keep those as
background only; the implementation must be local/no-write by default.

## Expected Shape

Add a no-write branch-or-PR readiness command. Suggested naming:

- CLI: `scripts/repo_contract_kit.py branch-readiness --repo <repo> --json`
- installed Make target: `make agent-branch-readiness BRANCH_READY_JSON=1`

The worker may choose a clearer local name if the command is documented and
tested, but it must not collide with `agent-task-ready`.

Readiness JSON should include:

- `schema_version`
- `command`
- `repo_root`
- target/base/head ref metadata
- `ready: true|false`
- result enum such as `ready`, `not-ready`, `blocked`, or `unknown`
- `blockers`
- `warnings`
- local evidence sections
- optional CI/check evidence
- optional receipt/review disposition evidence
- `target_repo_writes: false`
- `sidecar_writes: false`
- `next_safe_commands`

Local evidence should aggregate, where available:

- git cleanliness and changed files
- base freshness or base-ref relationship
- docs-impact status and explicit no-docs-needed waiver state
- changelog/version check state for release-impacting changes
- strict receipt validation or review disposition input
- task readiness/finalizer references when the branch started from prepared
  task metadata
- state-ledger or task-status signals when relevant

Optional CI/check input should be local and explicit, for example a JSON file or
CLI flags. It should be able to represent required and advisory checks with
states such as success, pending, failed, skipped, missing, and unknown.
Pending, failed, missing, or unknown required checks should block readiness
unless explicitly marked advisory or omitted with a warning.

The command should not call GitHub by default. It may consume a JSON export from
another tool, but AGW-052 should not implement hosted polling, PR mutation,
merge queue control, or branch-protection configuration.

## Non-Goals

- No merge, approve, label, PR comment, enqueue/dequeue, or branch mutation.
- No default GitHub credentials, API calls, network polling, or hosted CI loops.
- No replacement for `agent-task-ready`; aggregate or reference that evidence
  when it exists.
- No `AGW-053` merge-governance examples.
- No provider-specific CI dependency.
- No weakening docs-impact, receipt, task-status, dirty-state, or
  version/changelog gates.

## Acceptance

1. `repo-contract-kit` exposes a branch-or-PR readiness command through the
   AI-first CLI and installed Makefile surface.
2. Readiness JSON aggregates local evidence into ready/not-ready, blockers,
   warnings, and next safe commands without target or sidecar writes by
   default.
3. Docs-impact and waiver state affect readiness: missing required docs without
   waiver blocks, covered docs pass, and explicit `No docs needed:` is recorded.
4. Optional CI/check input can mark required checks success, pending, failed,
   skipped, missing, or unknown; pending/failing/missing required checks block
   readiness.
5. Receipt or review disposition input is validated when provided and can block
   readiness when evidence is invalid or failing.
6. The command does not merge, approve, comment, call GitHub, enqueue merge
   queues, or edit branch-protection settings.
7. Docs explain the command's relationship to `agent-task-ready`, finalizer,
   branch protection, status checks, and `AGW-053` merge-governance examples.
8. Version/changelog and source backlog rows close `AGW-052` after validation.

## Required Validation

Run in `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_repo_contract_kit_cli tests.test_install tests.test_agent_task_ready`
- any new focused test module added for branch/PR readiness
- `PYTHONDONTWRITEBYTECODE=1 make test`
- `make docs-check`
- `make docs-freshness`
- `make version-check`
- `git diff --check`

Run in `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview` after source closeout:

- `make backlog-check`
- `make backlog-split-check`
- `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
- `git diff --check`

Expected version decision: patch bump and changelog entry in
`repo-contract-kit`, because this adds a user-facing CLI/Make readiness
surface.

Capture:

- focused and full kit test output
- sample readiness JSON for a ready branch and a blocked branch
- no-write proof for the default command
- docs-impact, docs-freshness, and version-check output
- source backlog validation output
- `git diff --name-only` for both repos
- remote ref match after pushes
- final clean status for both checkouts

## Documentation Impact

- Expected: `yes`
- Paths:
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/README.md`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/common/working-rhythm.md`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/common/ops-agent-workflow.md`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/common/harness-engineering.md`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/docs/harness-engineering.md`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/docs/rollout-guide.md`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/CHANGELOG.md`
  - source backlog summary files
- Waiver allowed: `no`

## Risk And Stop Conditions

Risk level: `medium`.

Known risks:

- Readiness can be mistaken for merge permission if docs do not separate local
  evidence from hosted governance.
- Optional CI/check inputs can create false readiness if unknown or stale data
  is treated as passing.
- Duplicating `agent-task-ready` logic can drift from the per-task gate.
- A command that shells out to many checks can become slow or non-deterministic
  if not scoped.

Stop if:

- implementation needs GitHub credentials, network polling, PR mutation, merge
  queue operations, or branch-protection edits;
- readiness output lacks explicit blockers/warnings and no-write metadata;
- required docs-impact or receipt evidence can be missing while `ready` remains
  true;
- full kit tests or source backlog checks fail.

## Closeout

- Commit and push `repo-contract-kit` `main`.
- Commit and push source backlog closeout in `agent-workflow-kit` after kit
  validation and push.
- Record or link a final receipt at
  `.agent-workflows/tasks/agw-052-branch-pr-readiness/receipt.json` or a
  durable sidecar equivalent when available.
- Use the new branch/PR readiness command on the AGW-052 branch if available;
  otherwise record why per-task `agent-task-ready` is not applicable to direct
  source checkout work.
- Run `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
  in `agent-workflow-kit`.
- Final handoff must say whether both checkouts are clean, only expected files
  remain dirty, cleanup is blocked, or unrelated dirt was preserved.
