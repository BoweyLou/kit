# AGW-131 Task Packet: Story-Level Task Packets

## Source

- Backlog item: `AGW-131`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Implementation commit: `c77200f`
- Released version: `repo-contract-kit` `0.6.23`
- Status: `done`

## Problem

Compact backlog rows were becoming executable task packets without enough
actor, operator, outcome, and acceptance context. That made agents rediscover
why a task existed and how to stop scope expansion during implementation.

## Scope

- Require machine-readable task packets to include a `story` block with a user
  story, operator story, or job-to-be-done shape.
- Require explicit non-goals in the task-packet schema so executable packets do
  not inherit unbounded scope from compact backlog mirrors.
- Add `--story-*` CLI overrides for direct `task-packet` and
  `agent-task-packet-from-backlog` scaffolds.
- Generate default operator stories for backlog-selected packets while keeping
  raw backlog rows compact.
- Add story context to local `agent-task-prepare` worktree packets.
- Update prompt, planning, harness, operator, generated CLI, version, and
  changelog docs.
- Add regression coverage for direct, backlog-derived, and task-worktree packet
  generation.

## Non-Goals

- Do not turn the backlog mirror into a full product/story-management surface.
- Do not require external planning systems to store the expanded story fields.
- Do not change unrelated task lifecycle, finalizer, or closeout behavior.

## Validation

- `python3 -m unittest tests.test_repo_contract_kit_cli.RepoContractKitCliTests.test_task_packet_emits_machine_readable_scaffold tests.test_repo_contract_kit_cli.RepoContractKitCliTests.test_task_packet_from_backlog_prefills_selected_item tests.test_agent_task_prepare.AgentTaskPrepareTests.test_prepare_creates_sibling_worktree_and_local_task_artifacts`
- `python3 -m unittest tests.test_repo_contract_kit_cli tests.test_agent_task_prepare tests.test_install`
- `make workflow-source-check`
- `make docs-freshness`
- `make docs-check`
- `make version-check`
- `git diff --check`
- `make test`

## Closeout Evidence

- `repo-contract-kit` commit `c77200f` releases version `0.6.23`.
- `templates/common/task-packet.schema.json` and
  `workflows/schemas/task-packet.schema.json` now require `story` and non-empty
  `context.non_goals`.
- `task-packet` and `agent-task-packet-from-backlog` accept `--story-type`,
  `--story-actor`, `--story-need`, `--story-outcome`, and
  `--story-acceptance-summary`.
- Backlog-derived packets get default operator stories from the selected row;
  task-worktree packets get write-worker story context.
- Full repo-contract-kit validation passed with `299` tests.
