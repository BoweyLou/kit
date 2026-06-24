# AGW-097 Task Packet: Agent State Ledger

## Task

- ID: `AGW-097`
- Title: Add a local agent-state ledger that indexes dirty-state, automation,
  task lifecycle, readiness, and closeout receipts.
- Priority: `P1`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv`

## Context

- Repository: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- Mode: `implementation`
- Problem statement: the kit now emits useful receipts and reports across
  preflight, automation handoff, task readiness, task finalization, closeout,
  dirty-primary baselines, and self-heal, but an agent still has to inspect
  several commands and sidecar directories to understand current state. Add one
  local ledger report that indexes those artifacts and tells agents what is
  unresolved and what command is safe to run next.
- Background:
  - `AGW-085` added preflight/doctor startup receipts.
  - `AGW-087` added finalizer receipts and lifecycle closeout.
  - `AGW-088` added automation baseline and blocked/passed sidecar receipts.
  - `AGW-092` added compact context bundles with sidecar and readiness hints.
  - `AGW-095` added dirty-primary task baselines.
  - `AGW-096` added guarded self-heal and sidecar before/after receipts.
- Non-goals:
  - Do not mutate task metadata, sidecar receipts, worktrees, or source files.
  - Do not replace `agent-task-status`, `agent-task-ready`,
    `agent-task-closeout`, `agent-self-heal`, or `agent-automation-handoff`.
  - Do not require a hosted service, external database, or network access.
  - Do not infer ownership beyond local metadata; thread/session attribution
    expansion remains `AGW-099`.

## Goal Alignment

- repo_goal: keep `repo-contract-kit` as the install-layer guardrail provider
  that gives agents deterministic local state reports and next-command guidance
  without hiding or mutating user work.
- area_contracts:
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/repo_contract_kit.py`
    purpose: target-repo CLI and sidecar orchestration for local reports and
    receipts.
    source: installed CLI and Make targets
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_status.py`
    purpose: authoritative task metadata, worktree, lease, and overlap report.
    source: installed `make agent-task-status`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_ready.py`
    purpose: readiness receipt validation, scope drift, freshness, and baseline
    drift report.
    source: installed `make agent-task-ready`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_cleanup.py`
    purpose: closeout and cleanup inventory for terminal task worktrees.
    source: installed `make agent-task-cleanup` and `make agent-task-closeout`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/kit-makefile.mk`
    purpose: installed target-repo Make surface for read-only state reports.
    source: installer tests and docs freshness
    status: `aligned`
- alignment_decision: `aligned`
- adaptation_needed: `no`
- stop_conditions:
  - Stop if the ledger would write, prune, quarantine, close, or mutate any
    local state.
  - Stop if the report cannot distinguish missing receipts, stale metadata,
    dirty worktrees, and automation blockers as separate categories.
  - Stop if implementation duplicates broad task/worktree logic instead of
    reusing or composing existing deterministic reports where practical.

## Scope

- Inspect first:
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/repo_contract_kit.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_status.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_ready.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_cleanup.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_finalize.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/kit-makefile.mk`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/working-rhythm.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/ops-agent-workflow.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/test_repo_contract_kit_cli.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/test_agent_task_prepare.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/test_agent_task_cleanup.py`
- Allowed edits:
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/repo_contract_kit.py`
  - Optional helper under
    `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/README.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/VERSION`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/CHANGELOG.md`
  - Source backlog closeout files in
    `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-workflow-review/`
    after kit validation passes.
- Protected:
  - All target-repo source files, task metadata, sidecar receipts, and worktrees
    during ledger generation.
  - Existing command semantics for preflight, self-heal, automation handoff,
    readiness, finalizer, status, and closeout.
  - Unrelated backlog rows.
- Expected outputs:
  - New read-only installed command, likely `make agent-state-ledger`, with JSON
    and concise text output.
  - Ledger sections for checkout dirty state, active/terminal/stale task
    metadata, task worktree status, final receipts, readiness/finalizer
    receipts, automation handoff receipts/baselines, self-heal receipts, and
    sidecar availability.
  - Per-task/session summary where local metadata exists: task id, status,
    owner/session id, worktree, dirty state, lease, final receipt, latest
    related receipts, unresolved blockers, and next safe command.
  - Repository-level unresolved blockers and warnings: dirty checkout,
    dirty/missing worktrees, stale metadata, missing final receipts, active
    overlaps, blocked automation receipts, missing sidecar, and missing
    readiness evidence.
  - Explicit no-write metadata in output (`target_repo_writes` and
    `sidecar_writes` false) so agents can call it safely at startup.
  - Docs, tests, version, changelog, and source backlog closeout.

## Coordination

- Active task count: `0` in the source repo before starting AGW-097.
- Active sibling tasks: none reported by `make agent-task-status TASK_STATUS_JSON=1`.
- Worker rule: use exactly one task worker for this backlog item. The worker
  owns kit implementation files only; the parent owns source task-packet and
  backlog closeout.

## Acceptance Criteria

- `agent-state-ledger` is read-only and performs no target or sidecar writes.
- JSON output includes sidecar paths, dirty-state summary, task metadata
  summary, receipt indexes, unresolved blockers/warnings, and next safe command.
- Text output is concise enough for startup use and highlights unresolved
  blockers before informational history.
- Receipt indexing covers at least preflight/doctor receipts, finalizer
  receipts, automation handoff receipts/baselines, and self-heal receipts when
  present in the sidecar.
- Task indexing reports missing worktrees, dirty worktrees, stale leases, missing
  final receipts, and active overlaps without mutating them.
- Ledger output gives deterministic next safe commands such as
  `make agent-self-heal`, `make agent-task-status`, `make agent-task-ready`,
  `make agent-task-finalize`, `make agent-task-closeout`, or
  `make agent-automation-handoff`, depending on the unresolved state.
- Tests cover clean state, missing sidecar, active task with missing/dirty
  worktree, terminal task with missing final receipt, sidecar receipt indexing,
  and no-write guarantees.
- Docs explain that the ledger is an index/report, not a cleanup or closeout
  command.
- `VERSION` and `CHANGELOG.md` record the kit behavior change.
- Source backlog rows and summary close `AGW-097` only after kit validation
  passes.

## Validation

- Required commands in `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_repo_contract_kit_cli`
  - Run any new focused ledger test module directly if created.
  - `PYTHONDONTWRITEBYTECODE=1 make test`
  - `make docs-check`
  - `make version-check`
  - `git diff --check`
- Required commands in `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview` after
  source closeout:
  - `make backlog-check`
  - `make backlog-split-check`
  - `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
  - `git diff --check`

## Documentation Impact

- Expected: `yes`
- Paths:
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/README.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/working-rhythm.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/ops-agent-workflow.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/harness-engineering.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/harness-engineering.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/CHANGELOG.md`
  - source backlog summary files
- Waiver allowed: `no`

## Risk And Approval

- Risk level: `medium`
- Known risks:
  - A ledger can become noisy if it dumps every receipt instead of indexing the
    latest relevant state.
  - Receipt schema variants may differ across commands; parsing must tolerate
    old or partial receipts.
  - Next-command recommendations must stay conservative and not imply mutation
    authority.
- Stop conditions:
  - The ledger needs to mutate local state to produce its report.
  - Receipt parsing failures crash the command instead of becoming warnings.
  - The command hides missing receipts or stale task metadata behind a generic
    dirty-state result.
- Human approval:
  - Approval needed: `no`
  - State: `approved`
  - Approver/notes: User asked to implement all remaining workflow-stack backlog
    items serially with one task agent per backlog item.

## Handoff

- Recommended prompt: `workflows/prompts/task-packet.md`, then
  `workflows/prompts/verification-sentinel.md`
- Owner: one kit worker for implementation; parent for integration and closeout
