# AGW-090 Task Packet: Goal Alignment Contract

## Task

- ID: `AGW-090`
- Title: Define a repo and area goal-alignment contract for task packets.
- Priority: `P1`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv`

## Context

- Repository: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Mode: `verification`
- Problem statement: task packets constrain scope, docs impact, validation, approval, and closeout evidence, but they do not require each task to reconcile with a repository aim or the purpose of the affected folder area. That gap lets agents start narrowly scoped work that may still be misaligned, or miss the moment when an area goal needs to adapt.
- Background:
  - `AGW-089` made task-packet closeout evidence explicit in the prompt, template, and schema.
  - `docs/harness-engineering.md` frames task packets as the source-side contract that prevents broad requests from becoming unbounded edits.
  - `docs/working-rhythm.md` already positions task packets as the scope handoff before write-capable work.
  - `AGW-091` will separately add deterministic area-contract discovery and goal-check reporting in `repo-contract-kit`; this packet is the source-side contract that such reports should feed.
  - Canonical prompt edits start under `workflows/prompts/`; `.codex/prompts/` is generated and must be refreshed through `make prompt-adapters-export`.
- Non-goals:
  - Do not implement deterministic area-contract discovery, `make area-check`, or `make goal-check`; that is `AGW-091`.
  - Do not edit `AGENTS.md`; keep it as a route map rather than adding detailed goal-alignment rules there.
  - Do not create a backlog UI, hosted service, or external memory dependency.
  - Do not update managed install-layer scripts in this source repo unless a current validation producer requires a source-owned fixture update.

## Goal Alignment

- repo_goal: keep `agent-workflow-kit` as the source of truth for portable
  workflow prompts, schemas, task-packet contracts, regression fixtures, and
  source-side docs while leaving installed execution commands to
  `repo-contract-kit`.
- area_contracts:
  - path: `workflows/prompts/task-packet.md`,
    `workflows/prompts/templates/task-packet.md`
    purpose: canonical task-packet planning prompt and human-readable packet
    template.
    source: `AGENTS.md`; `docs/harness-engineering.md`;
    `workflows/prompts/README.md`
    status: `aligned`
  - path: `schemas/task-packet.schema.json`
    purpose: machine-readable source-side task packet contract for handoff
    artifacts.
    source: `workflows/prompts/README.md`; `docs/harness-engineering.md`
    status: `aligned`
  - path: `scripts/validate_agentic_regression_artifacts.py`
    purpose: source-owned regression fixture validator and generated packet
    materializer used by `make validate`.
    source: `scripts/validate_agentic_regression_artifacts.py`; `Makefile`
    status: `aligned`
  - path: `docs/`, `research/agentic-workflow-review/`, `VERSION`,
    `CHANGELOG.md`
    purpose: source-side operator documentation, backlog evidence, and release
    accounting for workflow contract changes.
    source: `AGENTS.md`; `docs/working-rhythm.md`
    status: `aligned`
- alignment_decision: `aligned`
- adaptation_needed: `no`
- stop_conditions:
  - Stop if implementation requires modifying `AGENTS.md` instead of source
    prompts/docs.
  - Stop if implementation requires changing managed installed commands or
    target-repo scripts; split that work to `AGW-091` or a companion kit packet.
  - Stop if an affected area purpose is unknown, conflicting, or requires goal
    adaptation without user approval.

## Scope

- Inspect first:
  - `workflows/prompts/task-packet.md`
  - `workflows/prompts/templates/task-packet.md`
  - `schemas/task-packet.schema.json`
  - `scripts/validate_agentic_regression_artifacts.py`
  - `tests/test_research_workflow_artifacts.py`
  - `docs/harness-engineering.md`
  - `docs/working-rhythm.md`
  - `workflows/prompts/README.md`
- Allowed edits:
  - `workflows/prompts/task-packet.md`
  - `workflows/prompts/templates/task-packet.md`
  - generated Codex adapters under `.codex/prompts/` via `make prompt-adapters-export`
  - `schemas/task-packet.schema.json`
  - `scripts/validate_agentic_regression_artifacts.py` if generated regression task packets need the new schema field
  - focused tests under `tests/`
  - docs that explain the task-packet goal-alignment contract
  - `VERSION` and `CHANGELOG.md`
  - backlog closeout rows and summary after validation passes
- Protected:
  - `AGENTS.md`
  - managed install-layer scripts such as `scripts/agent_task_prepare.py` and `scripts/repo_contract_kit.py`
  - companion `repo-contract-kit` checkout except for a separate explicitly accepted kit task
  - unrelated prompt families outside task-packet prompts and generated adapter mirrors
  - unrelated backlog rows
- Expected outputs:
  - Task-packet prompt requires a repo goal, area contracts for affected paths, alignment decision, adaptation-needed flag, and stop conditions before implementation handoff.
  - Task-packet template has a dedicated goal-alignment section with concise fields rather than burying the decision in background prose.
  - Task-packet schema validates a structured goal-alignment object containing `repo_goal`, `area_contracts`, `alignment_decision`, and `adaptation_needed`.
  - Source-owned generated task-packet fixtures include the new goal-alignment fields if schema validation requires them.
  - Docs explain that source-side task packets record the goal decision now, while deterministic installed reports arrive in `AGW-091`.

## Coordination

- Active task count: `0`
- Active sibling tasks: none reported by `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1` at packet creation.
- Registered external worktrees: existing registered worktrees are outside this packet; do not modify or clean them from this task.
- Overlap warnings: none for the primary checkout.

## Harness Metrics

- Context file count: `8`
- Token budget:
  - Keep the contract compact: goal summary, affected area path/purpose pairs, decision enum, adaptation flag, and stop conditions.
  - Do not ask task packets to copy long strategy docs or whole folder READMEs; reference sources and summarize the local alignment decision.

## Acceptance Criteria

- `workflows/prompts/task-packet.md` instructs planners to capture repo goal, affected area contracts, alignment decision, adaptation need, and stop conditions before handoff - verify by reading prompt source and generated adapter.
- `workflows/prompts/templates/task-packet.md` contains a dedicated goal-alignment section that includes `repo_goal`, `area_contracts`, `alignment_decision`, and `adaptation_needed` equivalents - verify by reading template source and generated adapter.
- `schemas/task-packet.schema.json` validates a structured goal-alignment object with required `repo_goal`, `area_contracts`, `alignment_decision`, and `adaptation_needed` fields - verify with focused tests and schema inspection.
- Schema-related fixture or task-packet generators that run in `make validate` emit valid goal-alignment defaults - verify with `scripts/validate_agentic_regression_artifacts.py` and focused tests.
- Docs explain how the contract helps agents stop or escalate when a task conflicts with repo or area goals, and distinguish this source-side contract from `AGW-091` deterministic installed reporting - verify changed docs.
- `make prompt-adapters-export` is run after prompt edits and `make prompt-adapters-check` passes - verify command output.
- The backlog row can be closed with evidence from focused tests, adapter checks, backlog checks, and `make agent-verify`.

## Validation

- Required commands:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_task_packet_contract`
  - `PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_agentic_regression_artifacts.py`
  - `PYTHONDONTWRITEBYTECODE=1 make prompt-adapters-check`
  - `make backlog-check`
  - `make backlog-split-check`
  - `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
  - `git diff --check`
- Evidence to capture:
  - Focused task-packet contract test output.
  - Agentic regression artifact validation output.
  - Prompt adapter export/check output.
  - Backlog status after closeout.
  - Agent verification output.
  - Diff summary and dirty-state explanation.

## Closeout Requirements

- Final receipt path: `.agent-workflows/tasks/agw-090-goal-alignment-contract/receipt.json` or sidecar equivalent.
- Readiness check:
  - Command: `make agent-task-ready TASK=AGW-090 TASK_READY_JSON=1` or record why unavailable for this non-worktree parent-run packet.
  - Expected result: ready report passes or blocker is recorded.
- Lifecycle action:
  - Action: `finish`
  - Command: `make agent-task-finish TASK=AGW-090 TASK_RECEIPT=<path> TASK_LIFECYCLE_JSON=1` or lifecycle fallback.
  - Expected result: metadata is closed and final receipt is linked, or fallback receipt is durable.
- Final task status:
  - Command: `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
  - Expected result: task is terminal or no local metadata was created and the reason is recorded.
- Closeout preview:
  - Command: `make agent-task-closeout TASK_CLOSEOUT_JSON=1`
  - Expected result: eligible, retained, or blocked cleanup state is recorded.
  - Apply requires explicit approval: `yes`
- Dirty-state explanation:
  - Final handoff must say whether the checkout is clean, only expected files are dirty, cleanup is blocked, or unrelated dirt was preserved.

## Documentation Impact

- Expected: `yes`
- Paths:
  - `workflows/prompts/README.md`
  - `docs/harness-engineering.md`
  - `docs/working-rhythm.md`
  - `CHANGELOG.md`
- Waiver allowed: `no`
- Notes: This changes the source task-packet contract and generated prompt adapter behavior.

## Risk And Approval

- Risk level: `medium`
- Known risks:
  - An overly broad goal-alignment section can become another prompt-tax field instead of a concrete start/stop decision.
  - Requiring area contracts before `AGW-091` exists can force agents to invent deterministic reports; this packet should allow manual summary with explicit unknowns.
  - Schema changes affect generated regression task packets and any local validations that consume `schemas/task-packet.schema.json`.
- Stop conditions:
  - Implementation requires modifying `AGENTS.md` instead of source prompts/docs.
  - Implementation requires changing `repo-contract-kit` managed scripts or installed Make targets; split to `AGW-091` or a companion kit packet.
  - Prompt adapter generation produces unexpected changes outside task-packet prompt files.
  - A task conflicts with a declared repo or area goal and no user approval exists to adapt the goal.
- Human approval:
  - Approval needed: `no`
  - State: `approved`
  - Approver/notes: Active user goal is to implement remaining backlog items serially with one task agent per item.

## Handoff

- Recommended prompt: `workflows/prompts/task-packet.md`, then `workflows/prompts/verification-sentinel.md`
- Owner: one worker agent
- Dependencies:
  - `AGW-089` closeout evidence contract.
  - `AGW-091` follow-up for deterministic installed area-contract discovery.
- Next packet hint: `AGW-091` should implement deterministic installed reports that can populate the new task-packet goal-alignment fields.
