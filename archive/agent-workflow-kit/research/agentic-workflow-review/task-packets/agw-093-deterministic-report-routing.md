# AGW-093 Task Packet: Deterministic Report Routing

## Task

- ID: `AGW-093`
- Title: Teach prompts and fixtures to prefer deterministic reports over broad repo rereads.
- Priority: `P1`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv`

## Context

- Repository: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Mode: `verification`
- Problem statement: the workflow stack now has deterministic reports for
  startup, backlog, task state, docs impact, token budgets, goal alignment, and
  compact context bundles, but source prompts can still ask agents to rediscover
  the same facts through broad repo rereads. Prompt contracts and fixtures need
  to route agents through compact reports first and preserve evidence fields
  when escalation is needed.
- Background:
  - `AGW-056` added agentic regression fixtures.
  - `AGW-072` added token-budget reporting and context-economy guidance.
  - `AGW-074` added harness metrics to packets/receipts.
  - `AGW-090` added task-packet goal alignment.
  - `AGW-092` added installed `agent-context-bundle` / `make agent-context-bundle`.
  - `docs/harness-engineering.md` maps source and installed harness surfaces.
- Non-goals:
  - Do not add new installed kit commands; this is source prompt and fixture
    work.
  - Do not change repo-contract-kit in this packet.
  - Do not remove the ability to inspect source files when deterministic
    reports are missing, ambiguous, stale, or show blockers.
  - Do not hide required evidence fields behind compact summaries.

## Goal Alignment

- repo_goal: keep `agent-workflow-kit` as the source of prompt, schema,
  fixture, and harness-design truth that tells agents how to consume installed
  deterministic reports.
- area_contracts:
  - path: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/`
    purpose: canonical prompt source for agent review, task, maintainer, and
    verification behavior.
    source: `AGENTS.md`; `docs/harness-engineering.md`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/.codex/prompts/`
    purpose: generated Codex adapter snapshot exported from canonical prompts.
    source: `Makefile prompt-adapters-export`; ADR 0002
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-regression-research/fixtures/`
    purpose: regression fixtures for known agentic workflow failure modes.
    source: `scripts/run_agentic_regression_fixtures.py`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/scripts/`
    purpose: deterministic validators and fixture runners for prompt/receipt
    contracts.
    source: `Makefile validate`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/docs/`
    purpose: source-side harness documentation and working rhythm.
    source: `docs/harness-engineering.md`
    status: `aligned`
- alignment_decision: `aligned`
- adaptation_needed: `no`
- stop_conditions:
  - Stop if the task requires editing installed repo-contract-kit behavior
    instead of source prompt/fixture contracts.
  - Stop if prompt routing would prevent agents from opening source files when
    compact reports are missing, stale, ambiguous, or blocked.
  - Stop if fixture updates weaken required evidence for scope, docs impact,
    goal alignment, validation, or receipts.

## Scope

- Inspect first:
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/task-packet.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/templates/task-packet.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/maintainer-queue.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/verification-sentinel.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/README.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-regression-research/fixtures/agentic-regression-seed.json`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/scripts/run_agentic_regression_fixtures.py`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/scripts/validate_agentic_regression_artifacts.py`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/docs/harness-engineering.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/docs/working-rhythm.md`
- Allowed edits:
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/.codex/prompts/` only through adapter export or exact generated-sync edits
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-regression-research/fixtures/`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/scripts/run_agentic_regression_fixtures.py`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/scripts/validate_agentic_regression_artifacts.py`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/tests/`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/docs/`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/VERSION`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/CHANGELOG.md`
  - Source backlog closeout files in `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-workflow-review/` after validation passes.
- Protected:
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/`
  - Source repo `AGENTS.md`, `REVIEW.md`, and `.agent-workflows/` runtime state
  - Unrelated backlog rows
  - Prompt adapter files without corresponding canonical prompt changes
- Expected outputs:
  - Prompt guidance that prefers `make agent-context-bundle`, `make agent-start`,
    `make goal-check`, `make agent-task-status`, `make agent-token-budget`, or
    equivalent deterministic reports before broad repo rereads.
  - Explicit escalation language: when reports are unavailable, stale, blocked,
    or ambiguous, agents inspect scoped source files and record what was missing.
  - Fixture runner/control updates that test deterministic report preference
    without dropping required evidence fields.
  - Updated docs and prompt adapters.
  - Version/changelog update for source prompt behavior.

## Coordination

- Active task count: `0` in the source repo after AGW-092 publication.
- Active sibling tasks: none reported by `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`.
- Overlap warnings: this task is source-side and should not edit the companion
  kit checkout. The parent will handle backlog closeout after validation.

## Harness Metrics

- Context file count: `10`
- Token budget:
  - Prefer short prompt deltas that route to report names and required fields
    rather than copying installed command output shapes into every prompt.
  - Fixture additions should assert preserved evidence, not large exemplar
    transcripts.

## Acceptance Criteria

- Source prompts route agents through compact deterministic reports first for
  startup, task packet, maintainer queue, and verification contexts, while still
  allowing scoped source inspection when reports are missing or ambiguous.
- Prompt/template guidance preserves required evidence for scope, goal
  alignment, docs impact, validation, closeout, receipts, and omissions.
- Agentic regression fixtures include a deterministic-report preference control
  or equivalent expected output, and the runner validates the relevant prompt
  and docs text.
- Generated `.codex/prompts/` adapters are synchronized from canonical
  `workflows/prompts/`.
- `VERSION` and `CHANGELOG.md` record the source behavior change.
- Source backlog rows and summary close `AGW-093` only after source validation
  passes.

## Validation

- Required commands in `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_prompt_regression_fixtures tests.test_task_packet_contract`
  - `PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_agentic_regression_fixtures.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_agentic_regression_artifacts.py`
  - `PYTHONDONTWRITEBYTECODE=1 make prompt-adapters-check`
  - `make backlog-check`
  - `make backlog-split-check`
  - `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
  - `git diff --check`
- Evidence to capture:
  - Focused prompt/fixture test output.
  - Adapter sync check output.
  - Full agent verification output.
  - Diff summary.
  - Dirty-state explanation.

## Closeout Requirements

- Final receipt path: `.agent-workflows/tasks/agw-093-deterministic-report-routing/receipt.json` or sidecar equivalent.
- Readiness check:
  - Command: `make agent-task-ready TASK=AGW-093 TASK_READY_JSON=1` or record why unavailable for this non-worktree parent-run packet.
  - Expected result: ready report passes or blocker is recorded.
- Lifecycle action:
  - Action: `finish`
  - Command: `make agent-task-finish TASK=AGW-093 TASK_RECEIPT=<path> TASK_LIFECYCLE_JSON=1` or lifecycle fallback.
  - Expected result: metadata is closed and final receipt is linked, or fallback receipt is durable.
- Final task status:
  - Command: `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
  - Expected result: task is terminal or no local metadata was created and the reason is recorded.
- Closeout preview:
  - Command: `make agent-task-closeout TASK_CLOSEOUT_JSON=1`
  - Expected result: eligible, retained, or blocked cleanup state is recorded.
  - Apply requires explicit approval: `yes`
- Dirty-state explanation:
  - Final handoff must say whether each checkout is clean, only expected files
    are dirty, cleanup is blocked, or unrelated dirt was preserved.

## Documentation Impact

- Expected: `yes`
- Paths:
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/README.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/docs/harness-engineering.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/docs/working-rhythm.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/CHANGELOG.md`
  - source backlog summary files
- Waiver allowed: `no`
- Notes: This changes source prompt behavior and regression controls.

## Risk And Approval

- Risk level: `medium`
- Known risks:
  - Prompts can over-trust compact reports and miss source-level evidence.
  - Fixtures can become string checks that pass while useful routing regresses.
  - Adapter files can drift if canonical prompts are edited without export.
  - Overly verbose report-routing rules can increase prompt footprint.
- Stop conditions:
  - The work expands into installed kit command changes.
  - The prompt changes remove required evidence or closeout fields.
  - The only way to validate the change is a broad manual read instead of
    deterministic fixture checks.
- Human approval:
  - Approval needed: `no`
  - State: `approved`
  - Approver/notes: Active user goal is to implement remaining backlog items
    serially with one task agent per item.

## Handoff

- Recommended prompt: `workflows/prompts/task-packet.md`, then
  `workflows/prompts/verification-sentinel.md`
- Owner: one worker agent
- Dependencies:
  - `AGW-092` installed context bundle.
  - Existing prompt adapter export/check flow.
  - Existing agentic regression fixture runner.
- Next packet hint: `AGW-094` should move to repo-contract-kit instruction diet
  auditing after source prompt routing is current.
