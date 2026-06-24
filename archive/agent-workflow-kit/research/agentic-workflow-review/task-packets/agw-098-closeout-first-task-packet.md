# AGW-098 Task Packet: Closeout-First Task Packet Contract

## Task

- ID: `AGW-098`
- Title: Add closeout-first task packet contract and refusal language for
  unfinished prior work.
- Priority: `P1`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv`

## Context

- Repository: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Mode: `verification`
- Problem statement: task packets now require closeout evidence at handoff, but
  a new implementation agent can still start from an unclosed previous packet
  unless source prompts make previous task state part of startup. Add a
  closeout-first contract that requires agents to identify unresolved prior
  task state, refuse or escalate unsafe starts, and record finalizer or blocker
  receipt paths before implementation begins.
- Background:
  - `AGW-084` added maintainer queue language for Active, Needs owner, Ready
    next, and Blocked work.
  - `AGW-087` added installed task finalizer receipts and lifecycle closeout.
  - `AGW-089` made closeout evidence required before task-packet handoff.
  - `AGW-093` taught source prompts to consume deterministic reports before
    broad repo rereads.
  - `AGW-097` added a read-only kit ledger in the companion repo, but this
    source checkout still reports installed `repo-contract-kit` 0.4.41 and does
    not currently expose `make agent-context-bundle` or `make agent-state-ledger`.
  - `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
    at packet creation reported `active_task_count: 0`, no hazards, no stale
    tasks, and no unknown-scope tasks.
  - `make agent-token-budget` at packet creation reported 97 files and 76259
    estimated tokens, result `passed`.
- Non-goals:
  - Do not add a new installed kit command; this is source prompt, schema,
    adapter, fixture, and docs work.
  - Do not refresh this repo's installed kit guardrail files unless the user
    separately asks for a kit update.
  - Do not auto-close, delete, prune, quarantine, or mutate stale task state.
    The source contract should route agents to finalizer, closeout, self-heal,
    blocker, or owner escalation paths instead.
  - Do not weaken existing goal alignment, docs impact, validation, closeout,
    or deterministic-report routing requirements.
  - Do not manage Codex desktop threads, credentials, PRs, or release tags.

## Previous Task State (`previous_task_state`)

- report_sources:
  - `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
  - `git log --oneline -1` at packet creation, showing AGW-097 source closeout
    commit `988b0dd`.
- active_tasks:
  - id: `none`
    state: `none`
    evidence: `agent-task-status` reported `active_task_count: 0`.
- unresolved_blockers:
  - `none reported`
- dirty_or_stale_state:
  - `none reported by agent-task-status at packet creation`
- finalizer_receipt_paths:
  - `source main commit 988b0dd62839a76ed361f8703bd6b8da60b6484e closed AGW-097; agent-task-status reported no active or stale tasks`
- blocker_receipt_paths:
  - `none`
- allowed_to_start: `yes`
- closeout_required_before_start:
  - decision: `safe-start`
  - reason: `AGW-097 was source-closed and task-status reported no active,
    stale, hazardous, or unknown-scope task state before AGW-098 implementation
    began.`
  - required_next_step: `Proceed with AGW-098 implementation; if task-status
    changes before edits, stop and refresh this gate.`
  - evidence_paths:
    - `research/agentic-workflow-review/task-packets/agw-098-closeout-first-task-packet.md`
    - `source main commit 988b0dd62839a76ed361f8703bd6b8da60b6484e`

## Goal Alignment

- repo_goal: keep `agent-workflow-kit` as the source of prompt, schema,
  fixture, and harness-design truth that tells agents how to start and close
  work from deterministic local evidence.
- area_contracts:
  - path: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/`
    purpose: canonical prompt source for agent startup, task-packet,
    implementation, maintainer, and verification behavior.
    source: `AGENTS.md`; `docs/harness-engineering.md`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/schemas/task-packet.schema.json`
    purpose: machine-readable source-side task packet handoff contract.
    source: `AGW-054`; `AGW-089`; `AGW-090`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/.codex/prompts/`
    purpose: generated Codex adapter snapshot exported from canonical prompts.
    source: `Makefile prompt-adapters-export`; ADR 0002
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-regression-research/fixtures/`
    purpose: regression fixtures for known agentic workflow failure modes.
    source: `scripts/run_agentic_regression_fixtures.py`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/docs/`
    purpose: source-side harness documentation and working rhythm.
    source: `docs/harness-engineering.md`; `docs/working-rhythm.md`
    status: `aligned`
- alignment_decision: `aligned`
- adaptation_needed: `no`
- stop_conditions:
  - Stop if the task requires changing installed `repo-contract-kit` command
    behavior instead of source prompt/schema contracts.
  - Stop if the prompt contract would tell agents to ignore unresolved active,
    stale, dirty, or blocked prior task state.
  - Stop if refusal language becomes broad permission to clean, reset, stash,
    or delete user work.
  - Stop if the schema change drops required closeout, goal-alignment, docs,
    validation, or evidence fields.

## Scope

- Inspect first:
  - `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
  - `make agent-token-budget`
  - `make kit-status`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/task-packet.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/templates/task-packet.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/fix-implementer.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/maintainer-queue.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/verification-sentinel.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/README.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/schemas/task-packet.schema.json`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-regression-research/fixtures/agentic-regression-seed.json`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/prompt-regression-fixtures/prompt-regression-fixtures.json`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/tests/`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/docs/harness-engineering.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/docs/working-rhythm.md`
- Allowed edits:
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/schemas/task-packet.schema.json`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/.codex/prompts/` only
    through adapter export or exact generated-sync edits
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-regression-research/fixtures/`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/prompt-regression-fixtures/`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/scripts/`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/tests/`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/docs/`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/VERSION`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/CHANGELOG.md`
  - Source backlog closeout files in
    `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-workflow-review/`
    after validation passes.
- Protected:
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/AGENTS.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/REVIEW.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/.agent-workflows/`
    runtime state, except reading deterministic reports
  - Unrelated backlog rows and unrelated dirty work
  - Prompt adapter files without corresponding canonical prompt changes
- Expected outputs:
  - Task-packet prompt and template require a `previous_task_state` section
    before implementation handoff.
  - `previous_task_state` captures at least report sources consulted, active
    tasks, unresolved blockers, dirty or stale task state, finalizer receipt
    paths, blocker receipt paths, and whether the next agent is allowed to
    start.
  - Prompt/template/schema add `closeout_required_before_start` as an explicit
    gate and make unsafe starts a refusal or escalation state.
  - Implementation-facing prompts, especially `fix-implementer.md`, tell agents
    to stop before edits when previous task closeout is missing, blocked, or
    ambiguous, and to report the exact command or receipt needed next.
  - Maintainer/verification prompts preserve the same closeout-first language
    so queue and review reports do not mark work ready while prior state is
    unresolved.
  - Regression fixtures or focused tests assert that the new fields are
    required and that refusal/escalation language is present.
  - Generated `.codex/prompts/` adapters are refreshed.
  - Docs, version, changelog, and source backlog closeout are updated.

## Coordination

- Active task count: `0` at packet creation.
- Active sibling tasks: none reported by
  `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`.
- Overlap warnings:
  - Source checkout installed kit is older than the companion kit; do not treat
    missing `agent-context-bundle` or `agent-state-ledger` targets in this
    checkout as a reason to edit kit files.
  - This is source-side prompt/schema work and should not edit
    `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/`.
  - Parent handles source task-packet commit, worker launch, integration,
    validation, commit, push, and backlog closeout.

## Harness Metrics

- Context file count: `14`
- Deterministic reports:
  - `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
    passed with zero active tasks and no hazards.
  - `make agent-token-budget` passed with 97 files and 76259 estimated tokens.
  - `make kit-status` reported installed `repo-contract-kit` 0.4.41 and target
    repo version 0.2.17.
  - `make agent-context-bundle` and `make agent-state-ledger` are unavailable in
    this source checkout at packet creation; record this as installed-kit drift,
    not an implementation blocker for source prompt work.
- Token budget:
  - Keep new prompt language compact and field-oriented.
  - Prefer references to report names, receipt paths, and decision states over
    embedding long command output examples.

## Acceptance Criteria

- `workflows/prompts/task-packet.md` and
  `workflows/prompts/templates/task-packet.md` require previous task state before
  handoff, including report sources, unresolved prior work, receipt paths, and
  start/stop decision.
- `schemas/task-packet.schema.json` requires a machine-readable
  `previous_task_state` object and `closeout_required_before_start` decision
  that can represent safe start, refusal, and blocker/escalation states.
- Implementation-facing prompts include refusal/escalation language that stops
  agents before editing when prior task closeout is missing, blocked,
  ambiguous, or unsafe.
- Maintainer and verification prompts avoid marking work ready when previous
  task state is unresolved and point to finalizer, task-status, closeout,
  self-heal, or owner escalation evidence.
- Regression fixtures or focused tests fail when a task packet omits the new
  previous-task and closeout-first fields, and pass for a valid packet with
  finalizer or blocker receipt evidence.
- Generated `.codex/prompts/` adapters match canonical prompt sources.
- `VERSION` and `CHANGELOG.md` record the source behavior change.
- Source backlog rows, split backlog, feature matrix or summary close `AGW-098`
  only after validation passes.

## Validation

- Required commands in `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_task_packet_contract`
  - Run any new focused task-packet schema or prompt regression test directly
    if created.
  - `PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_agentic_regression_fixtures.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_prompt_regression_fixtures.py`
  - `PYTHONDONTWRITEBYTECODE=1 make prompt-adapters-check`
  - `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
  - `make validate`
  - `make docs-lint`
  - `make docs-build`
  - `make docs-generate`
  - `python3 scripts/check_doc_impact.py`
  - `make version-check`
  - `make backlog-check`
  - `make backlog-split-check`
  - `git diff --check`
- Evidence to capture:
  - Focused schema/prompt test output.
  - Agentic and prompt regression fixture output.
  - Adapter sync check output.
  - Full source validation output.
  - Backlog and split-backlog validation after closeout.
  - Diff summary and dirty-state explanation.

## Closeout Requirements

- Final receipt path:
  `.agent-workflows/tasks/agw-098-closeout-first-task-packet/receipt.json` or
  sidecar equivalent.
- Readiness check:
  - Command: `make agent-task-ready TASK=AGW-098 TASK_READY_JSON=1` or record
    why unavailable for this parent-run packet.
  - Expected result: ready report passes or blocker is recorded.
- Lifecycle action:
  - Action: `finish`
  - Command: `make agent-task-finalize TASK=AGW-098 TASK_RECEIPT=<path> TASK_FINALIZE_JSON=1`
    or lifecycle fallback.
  - Expected result: metadata is closed and final receipt is linked, or fallback
    receipt is durable.
- Final task status:
  - Command: `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
  - Expected result: task is terminal or no local metadata was created and the
    reason is recorded.
- Closeout preview:
  - Command: `make agent-task-closeout TASK_CLOSEOUT_JSON=1`
  - Expected result: eligible, retained, or blocked cleanup state is recorded.
  - Apply requires explicit approval: `yes`
- Dirty-state explanation:
  - Final handoff must state whether the checkout is clean, only expected files
    are dirty, cleanup is blocked, or unrelated dirt was preserved.

## Documentation Impact

- Expected: `yes`
- Paths:
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/README.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/docs/harness-engineering.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/docs/working-rhythm.md`
  - `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/CHANGELOG.md`
  - Source backlog summary and feature matrix files
- Waiver allowed: `no`
- Notes: this changes source prompt behavior, task-packet schema, and agent
  startup expectations.

## Risk And Approval

- Risk level: `medium`
- Known risks:
  - Too-strong refusal wording could block safe work where prior state is clean
    but deterministic reports are unavailable.
  - Too-weak refusal wording could let agents keep starting on top of unfinished
    task state.
  - Schema changes can break existing packet fixtures if migrations are not
    handled deliberately.
  - Prompt additions can increase token footprint if they repeat long command
    examples instead of naming fields and report sources.
- Stop conditions:
  - The work expands into installed kit command behavior changes.
  - The schema cannot represent both safe-start and blocker-refusal states.
  - Existing valid packet fixtures cannot be updated without losing closeout,
    docs, validation, goal-alignment, or receipt evidence.
  - Validation reveals source installed-kit drift that must be resolved before
    prompt/schema work can be checked.
- Human approval:
  - Approval needed: `no`
  - State: `approved`
  - Approver/notes: User asked to implement remaining workflow-stack backlog
    items serially with one task agent per backlog item.

## Handoff

- Recommended prompt: `workflows/prompts/task-packet.md`, then
  `workflows/prompts/fix-implementer.md`, then
  `workflows/prompts/verification-sentinel.md`
- Owner: one worker agent for source implementation; parent for packet commit,
  integration, validation, push, and backlog closeout.
- Dependencies:
  - `AGW-087` installed finalizer semantics.
  - `AGW-089` task-packet closeout evidence contract.
  - `AGW-093` deterministic-report routing.
  - Existing prompt adapter export/check flow.
- Next packet hint: `AGW-099` should add installed thread/session attribution to
  task status, preflight, and dirty blockers in `repo-contract-kit`.
