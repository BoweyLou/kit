# AGW-096 Task Packet: Guarded Self-Heal

## Task

- ID: `AGW-096`
- Title: Add guarded agent self-heal for safe generated-state cleanup and stale
  metadata quarantine.
- Priority: `P1`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv`

## Context

- Repository: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- Mode: `implementation`
- Problem statement: agents now get better dirty-state explanations, baseline
  receipts, readiness gates, and closeout previews, but they still lack an
  approved recovery command for low-risk generated state. Without that command,
  agents either stop on dirty startup forever or improvise cleanup that could
  delete user work.
- Background:
  - `AGW-080` added guarded closeout for finished sibling task worktrees.
  - `AGW-085` added `agent-preflight` / `agent-doctor` with dirty-state and
    task/sidecar summaries.
  - `AGW-087` added `agent-task-finalize` so task metadata and receipts can be
    closed deliberately.
  - `AGW-088` and `AGW-095` added baseline receipts for original/primary dirty
    state so pre-existing dirt can be distinguished from new drift.
  - The user asked for self-heal paths and receipts so automations and agents
    can understand current state without mutating or hiding human work.
- Non-goals:
  - Do not clean, stash, revert, amend, or delete user source files.
  - Do not make self-heal run automatically from `agent-preflight`,
    `agent-task-prepare`, or automation handoff.
  - Do not remove clean terminal task worktrees; `agent-task-closeout` already
    owns guarded worktree removal.
  - Do not treat tracked source changes as generated artifacts unless the
    operator explicitly scopes those exact paths.

## Goal Alignment

- repo_goal: keep `repo-contract-kit` as the install-layer guardrail provider
  that gives agents explicit, receipt-backed recovery paths while preserving
  user work.
- area_contracts:
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/repo_contract_kit.py`
    purpose: target-repo CLI and sidecar orchestration for preflight,
    automation, context, and generated artifact commands.
    source: installed `make agent-preflight`, `make agent-doctor`, and sidecar
    receipts
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_status.py`
    purpose: report stale task metadata, missing worktrees, leases, and active
    coordination hazards.
    source: installed `make agent-task-status`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_cleanup.py`
    purpose: keep worktree cleanup separate from metadata/self-heal recovery.
    source: installed `make agent-task-cleanup` and `make agent-task-closeout`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/kit-makefile.mk`
    purpose: installed target-repo Make surface for operator-safe commands.
    source: installer tests and docs freshness
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/`
    purpose: operator-facing workflow guidance and harness map.
    source: docs contract
    status: `aligned`
- alignment_decision: `aligned`
- adaptation_needed: `no`
- stop_conditions:
  - Stop if the self-heal command needs to delete or alter tracked user source
    files without an exact operator-supplied path allowlist.
  - Stop if applying self-heal would remove task/worktree evidence instead of
    quarantining or receipt-recording it.
  - Stop if preview mode cannot prove the planned target and sidecar writes.

## Scope

- Inspect first:
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/repo_contract_kit.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_status.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_cleanup.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_lifecycle.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/kit-makefile.mk`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/working-rhythm.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/ops-agent-workflow.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/test_repo_contract_kit_cli.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/test_agent_task_cleanup.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/test_agent_task_status.py` if present
- Allowed edits:
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/repo_contract_kit.py`
  - Optional new helper script under
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
  - User project files outside generated kit, sidecar, task metadata, or
    operator-allowlisted paths.
  - Existing `agent-task-closeout` responsibility for removing task worktrees.
  - Existing dirty-primary baseline and automation-handoff baseline semantics.
  - Unrelated backlog rows.
- Expected outputs:
  - New installed command, likely `make agent-self-heal`, with CLI JSON/text
    output and an explicit apply flag such as `SELF_HEAL_APPLY=1`.
  - Preview default that inventories proposed repairs and performs no target or
    sidecar writes.
  - Narrow allowlist for apply-mode repairs, such as sidecar directory
    initialization, stale generated lock files, and stale terminal task metadata
    quarantine. Prefer quarantine/move with receipts over deletion.
  - Guard that refuses apply when unrelated tracked source changes are present;
    any tracked generated path exception must be exact, explicit, and recorded
    in the receipt.
  - Durable before/after receipt on apply, stored outside the target checkout
    when sidecar is available, with target_repo_writes and sidecar_writes paths.
  - Docs, tests, version, changelog, and source backlog closeout.

## Coordination

- Active task count: `0` in the source repo before starting AGW-096.
- Active sibling tasks: none reported by `make agent-task-status TASK_STATUS_JSON=1`.
- Worker rule: use exactly one task worker for this backlog item. The worker
  owns kit implementation files only; the parent owns source task-packet and
  backlog closeout.

## Acceptance Criteria

- `agent-self-heal` is preview-only by default and reports every proposed action
  before any mutation.
- Apply mode requires an explicit flag and writes a durable before/after receipt
  with target and sidecar paths.
- The command can initialize missing sidecar state without touching target
  source files.
- The command can quarantine stale terminal task metadata or stale generated
  task-state artifacts without deleting them.
- The command refuses apply when unrelated tracked source changes exist, unless
  the operator supplies exact scoped generated paths.
- The command refuses or reports unrecognized untracked files outside the
  generated-state allowlist instead of deleting them.
- Tests cover preview-no-write, apply receipt, sidecar-only repair,
  stale-metadata quarantine, tracked-source refusal, and allowed generated-path
  handling.
- Docs explain that self-heal is not a source cleanup, stash, reset, or worktree
  removal command.
- `VERSION` and `CHANGELOG.md` record the kit behavior change.
- Source backlog rows and summary close `AGW-096` only after kit validation
  passes.

## Validation

- Required commands in `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_repo_contract_kit_cli tests.test_agent_task_cleanup`
  - Run any new focused self-heal test module directly if created.
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

- Risk level: `medium-high`
- Known risks:
  - A self-heal command can be misread as permission to clean user work.
  - Quarantining metadata can hide active work if terminal/stale detection is
    too broad.
  - Sidecar receipts must remain local and avoid leaking source diffs beyond
    path/status metadata unless explicitly needed.
- Stop conditions:
  - The design requires broad delete/glob cleanup of repo contents.
  - The command cannot prove which paths it mutated.
  - The implementation overlaps with task-worktree removal instead of calling
    or deferring to `agent-task-closeout`.
- Human approval:
  - Approval needed: `no`
  - State: `approved`
  - Approver/notes: User asked to implement all remaining workflow-stack backlog
    items serially with one task agent per backlog item.

## Handoff

- Recommended prompt: `workflows/prompts/task-packet.md`, then
  `workflows/prompts/verification-sentinel.md`
- Owner: one kit worker for implementation; parent for integration and closeout
