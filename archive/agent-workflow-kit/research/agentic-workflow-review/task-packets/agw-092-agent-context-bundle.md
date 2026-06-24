# AGW-092 Task Packet: Agent Context Bundle

## Task

- ID: `AGW-092`
- Title: Add a deterministic compact context bundle for agent startup and task handoff.
- Priority: `P1`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv`

## Context

- Repository: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- Mode: `implementation`
- Problem statement: agents currently assemble startup and handoff context by
  running several deterministic reports separately, which burns context and
  leads to missing or duplicated evidence. The kit needs one bounded report that
  composes the existing local signals and explicitly lists omissions.
- Background:
  - `AGW-072` added installed token-budget reporting and source context-economy
    guidance.
  - `AGW-074` added harness metrics to task packets and receipts.
  - `AGW-090` added source-side task-packet goal alignment.
  - `AGW-091` added installed `goal-check` and area-contract reports.
  - Existing kit reports already cover docs impact, backlog status, next work,
    active task state, goal checks, startup packets, task readiness, and token
    budgets.
- Non-goals:
  - Do not change canonical source prompts for deterministic-report routing;
    that is `AGW-093`.
  - Do not add dirty-primary baselines, self-heal cleanup, or a global
    agent-state ledger; those are `AGW-095`, `AGW-096`, and `AGW-097`.
  - Do not build an LLM summarizer, hosted service, or external cache.
  - Do not hide omissions; size limits must report what was skipped or
    truncated.

## Goal Alignment

- repo_goal: keep `repo-contract-kit` responsible for installed target-repo
  execution surfaces that make workflow contracts deterministic, compact, and
  locally inspectable.
- area_contracts:
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/`
    purpose: installed CLI and target-repo scripts that emit deterministic
    harness reports.
    source: `docs/agent-workflow-stack.md`; `docs/harness-engineering.md`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/`
    purpose: managed target-repo templates for Make targets, schemas, docs, and
    local agent workflow config.
    source: `scripts/install.py`; `docs/repo-boundary.md`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/`
    purpose: regression coverage for installed CLI, installer, startup,
    readiness, and compact context behavior.
    source: `Makefile`; existing test modules
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/`
    purpose: operator-facing documentation for installed workflow commands.
    source: `docs/harness-engineering.md`; `docs/rollout-guide.md`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-workflow-review/`
    purpose: source-side backlog and packet records for cross-repo workflow
    stack work.
    source: `docs/agent-workflow-stack.md`
    status: `aligned`
- alignment_decision: `aligned`
- adaptation_needed: `no`
- stop_conditions:
  - Stop if the design requires source prompt changes rather than installed kit
    command/docs/test changes.
  - Stop if the bundle needs semantic LLM compression instead of deterministic
    field selection and truncation.
  - Stop if compact output hides blockers, dirty-state, unknown goal alignment,
    or missing receipts without an explicit omission entry.

## Scope

- Inspect first:
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/repo_contract_kit.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_start.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_prepare.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_ready.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_status.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/check_doc_impact.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/check_token_budget.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/goal_check.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/kit-makefile.mk`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/ops-agent-workflow.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/working-rhythm.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/harness-engineering.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/rollout-guide.md`
- Allowed edits:
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/README.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/VERSION`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/CHANGELOG.md`
  - Source backlog closeout files in `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-workflow-review/` after kit validation passes.
- Protected:
  - Canonical source prompt files under `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/`
  - Source repo `AGENTS.md`, `REVIEW.md`, and `.agent-workflows/` runtime state
  - Existing task lifecycle, readiness, docs-impact, and goal-check semantics
  - Hosted GitHub Actions behavior
  - Unrelated backlog rows
- Expected outputs:
  - An installed CLI report, preferably `repo_contract_kit.py agent-context-bundle`,
    with text and JSON output.
  - Installed `make agent-context-bundle` target.
  - Bundle sections for repo identity, dirty state, backlog/next work, active
    task state, changed-file docs impact, changed-file goal check,
    token-budget totals, validation/readiness hints, and sidecar paths when
    available.
  - Explicit size controls such as max files, max section chars, or max total
    chars with deterministic truncation and an `omissions` list.
  - JSON output stable enough for prompts and automations to consume without
    rereading broad docs.
  - Docs and tests covering clean repos, dirty repos, missing optional inputs,
    unknown goal-check areas, and truncation/omission behavior.

## Coordination

- Active task count: `0` in the source repo after AGW-091 publication.
- Active sibling tasks: none reported by `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`.
- Overlap warnings: this task edits the companion kit checkout plus source
  backlog records; keep commits separate by repo.

## Harness Metrics

- Context file count: `13`
- Token budget:
  - The new bundle is itself a context-economy artifact. Prefer field summaries,
    counts, paths, command names, and short notes over embedded long documents.
  - Include omission metadata whenever a section is skipped or truncated.

## Acceptance Criteria

- Installed repos expose `make agent-context-bundle` and an equivalent CLI JSON
  report - verify with installer/Make tests and CLI tests.
- The bundle composes existing deterministic signals for dirty state,
  backlog/next work, active task status, docs impact, goal check, token budget,
  and sidecar paths without weakening any existing gates - verify with focused
  CLI tests.
- JSON output has a stable schema with section statuses, source commands,
  compact payloads, and explicit omissions/truncation metadata - verify with
  regression tests.
- Text output is readable and bounded for agent startup handoff - verify with a
  CLI text-output test.
- Missing optional inputs such as absent backlog, absent area contracts, or no
  token-budget config produce warnings/omissions rather than crashes - verify
  with tests.
- `VERSION` and `CHANGELOG.md` in `repo-contract-kit` record the installed
  behavior.
- Source backlog rows and summary close `AGW-092` only after kit validation
  passes.

## Validation

- Required commands in `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_repo_contract_kit_cli`
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install tests.test_agent_start tests.test_agent_task_ready tests.test_agent_task_prepare tests.test_check_token_budget`
  - `PYTHONDONTWRITEBYTECODE=1 make test`
  - `make docs-check`
  - `make version-check`
  - `git diff --check`
- Required commands in `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview` after
  source backlog closeout:
  - `make backlog-check`
  - `make backlog-split-check`
  - `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
  - `git diff --check`
- Evidence to capture:
  - Focused CLI/install/start/readiness/status/token test output.
  - Full kit test/docs/version output.
  - Source backlog check and agent-verify output after closeout.
  - Diff summary for both repos.
  - Dirty-state explanation for both repos.

## Closeout Requirements

- Final receipt path: `.agent-workflows/tasks/agw-092-agent-context-bundle/receipt.json` or sidecar equivalent.
- Readiness check:
  - Command: `make agent-task-ready TASK=AGW-092 TASK_READY_JSON=1` or record why unavailable for this non-worktree parent-run packet.
  - Expected result: ready report passes or blocker is recorded.
- Lifecycle action:
  - Action: `finish`
  - Command: `make agent-task-finish TASK=AGW-092 TASK_RECEIPT=<path> TASK_LIFECYCLE_JSON=1` or lifecycle fallback.
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
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/README.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/harness-engineering.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/rollout-guide.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/working-rhythm.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/ops-agent-workflow.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/CHANGELOG.md`
  - source backlog summary files
- Waiver allowed: `no`
- Notes: This adds installed CLI/Make behavior and an operator-facing compact
  context contract.

## Risk And Approval

- Risk level: `medium`
- Known risks:
  - A bundle can become a dumping ground and recreate the token problem it is
    meant to solve.
  - Partial signals can be mistaken for gates if section statuses are unclear.
  - Truncation can hide blockers unless omissions are explicit and machine
    readable.
  - Reusing command internals can accidentally mutate sidecar or target repo
    state; the bundle should be read-only by default.
- Stop conditions:
  - The implementation requires prompt-source changes or belongs in `AGW-093`.
  - The implementation starts adding self-heal cleanup or dirty-primary baseline
    behavior.
  - The bundle cannot stay deterministic, bounded, and read-only.
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
  - `AGW-072` token-budget report.
  - `AGW-090` task-packet goal-alignment contract.
  - `AGW-091` installed goal-check report.
  - Existing backlog, task-status, doc-impact, and startup packet commands.
- Next packet hint: `AGW-093` should teach source prompts and fixtures to prefer
  this deterministic bundle before broad repo rereads.
