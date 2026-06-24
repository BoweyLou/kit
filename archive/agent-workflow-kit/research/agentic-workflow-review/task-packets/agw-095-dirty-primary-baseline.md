# AGW-095 Task Packet: Dirty Primary Baseline

## Task

- ID: `AGW-095`
- Title: Add dirty-primary baseline mode to task preparation.
- Priority: `P1`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv`

## Context

- Repository: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- Mode: `implementation`
- Problem statement: `agent-task-prepare` correctly blocks dirty primary
  checkouts by default, but safe isolated work can be blocked when the primary
  checkout already has unrelated dirt that the task will not touch. The kit
  needs an explicit baseline mode that records the current dirty state, allows
  isolated task work only by opt-in, and later proves whether the primary
  checkout changed after that baseline.
- Background:
  - `AGW-061` added task worktree preparation.
  - `AGW-085` and `AGW-086` added preflight/doctor and actionable dirty blockers.
  - `AGW-088` added original-checkout baseline comparison for automation handoff.
  - `AGW-092` added compact context bundles that surface dirty state and
    omissions.
  - The user reported on 2026-06-15 that automations and task starts fail when
    agents see unrelated dirty work in the target repo.
- Non-goals:
  - Do not weaken the default clean-primary safety gate.
  - Do not silently ignore dirty tracked or untracked work.
  - Do not mutate, stash, revert, or clean user files.
  - Do not make baseline mode the default for write-capable task preparation.

## Goal Alignment

- repo_goal: keep `repo-contract-kit` as the install-layer guardrail provider
  for target repos, with explicit opt-in recovery paths that preserve user work
  and produce receipts.
- area_contracts:
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_prepare.py`
    purpose: prepare isolated task worktrees and in-flight metadata for
    write-capable agents.
    source: installed `make agent-task-prepare`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_ready.py`
    purpose: verify handoff readiness for prepared task worktrees.
    source: installed `make agent-task-ready`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/kit-makefile.mk`
    purpose: installed target-repo Make surface for task preparation flags.
    source: installer tests and docs freshness
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/`
    purpose: operator-facing installed workflow and rollout guidance.
    source: docs contract
    status: `aligned`
- alignment_decision: `aligned`
- adaptation_needed: `no`
- stop_conditions:
  - Stop if baseline mode would allow task preparation without an explicit
    operator flag.
  - Stop if baseline metadata cannot prove whether the primary checkout changed
    after task preparation.
  - Stop if finalize/readiness/handoff logic cannot block or warn on primary
    drift after the baseline.

## Scope

- Inspect first:
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_prepare.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_ready.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_finalize.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/repo_contract_kit.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/kit-makefile.mk`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/working-rhythm.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/ops-agent-workflow.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/test_agent_task_prepare.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/test_agent_task_ready.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/test_agent_task_finalize.py`
- Allowed edits:
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_prepare.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_ready.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_finalize.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/repo_contract_kit.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/README.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/VERSION`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/CHANGELOG.md`
  - Source backlog closeout files in `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-workflow-review/` after kit validation passes.
- Protected:
  - User target repos outside the kit checkout.
  - Existing default clean-primary prepare behavior.
  - Unrelated task lifecycle, closeout, and automation-handoff semantics.
  - Unrelated backlog rows.
- Expected outputs:
  - Explicit baseline flag for `agent-task-prepare` / installed Make target,
    separate from the existing blunt `ALLOW_DIRTY=1` escape hatch.
  - Captured dirty-state baseline with tracked/untracked entries, counts, HEAD,
    and a deterministic state hash in task metadata and task packet/receipt
    evidence.
  - Readiness/finalize or handoff guard that compares current primary state to
    the stored baseline and blocks when it drifted after prepare.
  - JSON/text output that explains the baseline and safe next command.
  - Docs, tests, version, changelog, and source backlog closeout.

## Coordination

- Active task count: `0` in the source repo before starting AGW-095.
- Active sibling tasks: none reported by `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`.
- Worker rule: use exactly one task worker for this backlog item. The worker
  owns kit implementation files only; the parent owns source task-packet and
  backlog closeout.

## Acceptance Criteria

- Default `agent-task-prepare` still blocks dirty primary checkouts.
- A new explicit baseline mode allows preparation from a dirty primary checkout
  while recording the baseline in local task metadata and receipt scaffolds.
- The baseline includes enough deterministic evidence to compare later primary
  state: dirty entries, counts, HEAD, changed files, and state hash.
- Readiness/finalize or handoff checks block or report when the primary checkout
  changed after the baseline.
- Tests cover default blocking, baseline opt-in, matching-baseline success, and
  changed-since-baseline blocking.
- Docs explain when baseline mode is appropriate and that it does not clean or
  bless unrelated dirt.
- `VERSION` and `CHANGELOG.md` record the kit behavior change.
- Source backlog rows and summary close `AGW-095` only after kit validation
  passes.

## Validation

- Required commands in `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_agent_task_prepare tests.test_agent_task_ready tests.test_agent_task_finalize`
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
  - Baseline mode could be misread as permission to ignore unrelated user work.
  - Hashing untracked file contents must remain deterministic and local-only.
  - Drift checks must not block because the task worktree itself changed; they
    must compare the primary checkout baseline.
- Stop conditions:
  - The design requires force-cleaning, stashing, or modifying user dirty files.
  - The guard cannot distinguish matching pre-existing dirt from new primary
    checkout drift.
  - The change would make dirty baseline mode implicit or automatic.
- Human approval:
  - Approval needed: `no`
  - State: `approved`
  - Approver/notes: User asked to implement all remaining workflow-stack backlog
    items serially with one task agent per backlog item.

## Handoff

- Recommended prompt: `workflows/prompts/task-packet.md`, then
  `workflows/prompts/verification-sentinel.md`
- Owner: one kit worker for implementation; parent for integration and closeout
