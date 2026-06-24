# AGW-099 Task Packet: Thread And Session Attribution

## Task

- ID: `AGW-099`
- Title: Add thread and session attribution to task status, preflight, and dirty
  blockers.
- Priority: `P1`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv`

## Context

- Repository: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- Mode: `verification`
- Problem statement: when parallel Codex threads, task workers, or automations
  touch the same repo, dirty-state blockers still read as anonymous local dirt.
  The kit already records owner/session values in task metadata, but status,
  preflight/doctor, ledger, and prepare blockers need a richer local attribution
  object so agents can identify the likely owner/session/task/automation before
  deciding whether to wait, finalize, self-heal, or escalate.
- Background:
  - `AGW-066` added task status for active metadata and worktrees.
  - `AGW-067` added task lifecycle owner/session updates.
  - `AGW-085` and `AGW-086` made preflight and dirty prepare blockers
    actionable.
  - `AGW-087` added finalizer receipts.
  - `AGW-095` added dirty-primary baselines.
  - `AGW-097` added a read-only state ledger that indexes task metadata,
    receipts, dirty state, and next safe commands.
  - The kit checkout is clean at `f1a628c` (`repo-contract-kit` 0.4.47), and
    `make version-check && make docs-check` passed at packet creation.
- Non-goals:
  - Do not inspect Codex Desktop internals, OS process tables, browser state, or
    remote service state to discover thread identities.
  - Do not expose private transcript content or cross-repo user data.
  - Do not make attribution authoritative when local metadata is missing.
  - Do not change task isolation, lifecycle status semantics, closeout removal,
    or dirty-primary baseline safety gates except to add provenance fields to
    reports and receipts.
  - Do not edit source prompt contracts in `agent-workflow-kit` beyond source
    backlog closeout after kit validation passes.

## Previous Task State (`previous_task_state`)

- report_sources:
  - `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
  - source `make agent-next`
  - source remote ref verification for AGW-098 commit `3336b38`
- active_tasks:
  - id: `none`
    state: `none`
    evidence: source `agent-task-status` reported `active_task_count: 0`.
- unresolved_blockers:
  - `none reported`
- dirty_or_stale_state:
  - `none reported by source agent-task-status at packet creation`
- finalizer_receipt_paths:
  - `source main commit 3336b3808b539af94bca3db932b5bb986babd4b5 closed AGW-098; source agent-task-status reported no active or stale tasks`
- blocker_receipt_paths:
  - `none`
- allowed_to_start: `yes`
- closeout_required_before_start:
  - decision: `safe-start`
  - reason: `AGW-098 was source-closed and source task-status reported no
    active, stale, hazardous, or unknown-scope task state before AGW-099 packet
    creation.`
  - required_next_step: `Proceed with AGW-099 packet and one kit worker; refresh
    task-status if source or kit state becomes dirty before worker launch.`
  - evidence_paths:
    - `research/agentic-workflow-review/task-packets/agw-099-thread-session-attribution.md`
    - `source main commit 3336b3808b539af94bca3db932b5bb986babd4b5`

## Goal Alignment

- repo_goal: keep `repo-contract-kit` as the install-layer guardrail provider
  that helps local agents understand dirty state, task ownership, and safe next
  commands without mutating or exposing user work.
- area_contracts:
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_status.py`
    purpose: authoritative active task, worktree, owner/session, lease, dirty,
    stale, and overlap report.
    source: installed `make agent-task-status`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_prepare.py`
    purpose: create task metadata and dirty-start blocker output before
    write-capable work.
    source: installed `make agent-task-prepare`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/repo_contract_kit.py`
    purpose: CLI surfaces for preflight/doctor, state ledger, context bundle,
    automation handoff, and task-packet scaffolding.
    source: installed CLI and Make targets
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/kit-makefile.mk`
    purpose: target-repo Make variables for owner/session/attribution fields.
    source: installer tests and docs freshness
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/`
    purpose: installed operator docs and harness guidance.
    source: docs contract
    status: `aligned`
- alignment_decision: `aligned`
- adaptation_needed: `no`
- stop_conditions:
  - Stop if the design requires reading private Codex app state or external
    account data.
  - Stop if attribution would be presented as certain when it is only inferred
    from local metadata or receipts.
  - Stop if dirty blockers become permission to clean, stash, reset, or delete
    someone else's work.

## Scope

- Inspect first:
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_status.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_prepare.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_lifecycle.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_finalize.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/repo_contract_kit.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/kit-makefile.mk`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/working-rhythm.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/ops-agent-workflow.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/harness-engineering.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/test_agent_task_prepare.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/test_agent_task_finalize.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/test_repo_contract_kit_cli.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/test_agent_state_ledger.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/test_install.py`
- Allowed edits:
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_status.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_prepare.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_lifecycle.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_finalize.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/repo_contract_kit.py`
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
  - Runtime task metadata or sidecar receipts in real target repos.
  - Existing safety behavior for prepare, preflight, readiness, finalizer,
    closeout, automation handoff, and self-heal.
  - Source prompt/schema contracts from `agent-workflow-kit`.
  - Unrelated backlog rows.
- Expected outputs:
  - A local attribution object used consistently in task metadata/report output,
    with optional `owner`, `owner_label`, `session_id`, `thread_id`,
    `automation_id`, `run_id`, metadata path, latest receipt path, and an
    explicit confidence such as `metadata`, `receipt`, `inferred`, or `unknown`.
  - `agent-task-prepare` and installed Make variables accept and persist the new
    attribution fields while preserving existing `TASK_OWNER` and
    `TASK_SESSION_ID`.
  - `agent-task-status` JSON/text reports attribution per task and groups
    hazards/stale/unknown-scope/dirty task worktree blockers by likely owner.
  - `agent-preflight` / `agent-doctor` JSON/text reports dirty checkout,
    sibling-worktree, missing-worktree, and active-task blockers with local
    attribution where available, and `unknown` when no local evidence exists.
  - `agent-state-ledger` carries the same attribution object and last receipt
    provenance for tasks and unresolved blockers.
  - Docs and tests cover manual task attribution, automation attribution, and
    missing-attribution fallback without leaking private data.
  - `VERSION` and `CHANGELOG.md` record the kit behavior change.

## Coordination

- Active task count: `0` in the source repo before packet creation.
- Active sibling tasks: none reported by source
  `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`.
- Overlap warnings:
  - AGW-099 edits the kit checkout and source closeout metadata only after kit
    validation.
  - Use exactly one kit worker for implementation. The worker owns kit
    implementation files only; parent owns source packet and source backlog
    closeout.

## Harness Metrics

- Context file count: `18`
- Deterministic reports:
  - Source `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
    passed with zero active tasks, no hazards, no stale tasks, and no
    unknown-scope tasks.
  - Source `make agent-token-budget` passed with 97 files and 77458 estimated
    tokens.
  - Kit `make version-check && make docs-check` passed at `repo-contract-kit`
    0.4.47.
- Token budget:
  - Keep attribution docs and output compact; prefer one nested attribution
    object over duplicating owner/session/thread fields in every warning string.

## Acceptance Criteria

- Task metadata and lifecycle updates can persist optional `thread_id`,
  `automation_id`, and `owner_label` without breaking existing owner/session
  fields.
- `agent-task-status` JSON includes attribution for each task and for
  coordination hazards/stale/unknown-scope/dirty-worktree blockers when local
  metadata is available; text output names owner/session/thread/automation in a
  concise line.
- Dirty prepare blockers and `agent-preflight`/`agent-doctor` include an
  attribution section that distinguishes current checkout dirt, attributed task
  worktree dirt, automation-attributed receipt blockers, and unknown local dirt.
- `agent-state-ledger` carries attribution and latest receipt provenance in
  task summaries and unresolved blockers/warnings, and next commands remain
  conservative.
- Missing attribution is explicit (`unknown`) and does not infer from private
  transcripts, external apps, or remote services.
- Tests cover manual task attribution, automation attribution, missing
  attribution fallback, dirty/preflight blocker attribution, and ledger/status
  rendering.
- Docs explain privacy/local-only boundaries and how agents should use
  attribution before starting, blocking, waiting, or escalating.
- `VERSION` and `CHANGELOG.md` record the kit behavior change.
- Source backlog rows and summary close `AGW-099` only after kit validation
  passes.

## Validation

- Required commands in `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_agent_task_prepare tests.test_agent_task_finalize tests.test_repo_contract_kit_cli tests.test_agent_state_ledger tests.test_install`
  - Run any new focused attribution test module directly if created.
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

## Closeout Requirements

- Final receipt path:
  `.agent-workflows/tasks/agw-099-thread-session-attribution/receipt.json` or
  sidecar equivalent.
- Readiness check:
  - Command: `make agent-task-ready TASK=AGW-099 TASK_READY_JSON=1` or record
    why unavailable for this parent-run packet.
  - Expected result: ready report passes or blocker is recorded.
- Lifecycle action:
  - Action: `finish`
  - Command: `make agent-task-finalize TASK=AGW-099 TASK_RECEIPT=<path> TASK_FINALIZE_JSON=1`
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
  - Final handoff must state whether source and kit checkouts are clean, only
    expected files are dirty, cleanup is blocked, or unrelated dirt was
    preserved.

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
- Notes: this changes installed report/output semantics and task metadata
  provenance.

## Risk And Approval

- Risk level: `medium`
- Known risks:
  - Agents may over-trust local attribution and blame the wrong owner if
    metadata is stale.
  - Extra fields can bloat reports if duplicated instead of nested.
  - Privacy boundaries matter: thread/session ids should remain local metadata,
    not transcript or remote account data.
- Stop conditions:
  - The design requires accessing Codex Desktop databases, OS process state, or
    remote services.
  - Attribution cannot be represented as optional or unknown.
  - Tests cannot prove existing owner/session fields remain backward
    compatible.
- Human approval:
  - Approval needed: `no`
  - State: `approved`
  - Approver/notes: User asked to implement remaining workflow-stack backlog
    items serially with one task agent per backlog item.

## Handoff

- Recommended prompt: `workflows/prompts/task-packet.md`, then
  `workflows/prompts/verification-sentinel.md`
- Owner: one kit worker for implementation; parent for integration and closeout
- Dependencies:
  - `AGW-066` task status.
  - `AGW-067` lifecycle owner/session metadata.
  - `AGW-085`/`AGW-086` preflight and dirty-start blocker detail.
  - `AGW-087` finalizer receipts.
  - `AGW-097` state ledger.
- Next packet hint: continue to the next open source backlog item after AGW-099
  is validated and closed.
