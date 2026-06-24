# AGW-094 Task Packet: Instruction Diet Audit

## Task

- ID: `AGW-094`
- Title: Add an instruction diet audit that proposes offloading detail out of agent-facing docs.
- Priority: `P1`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv`

## Context

- Repository: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- Mode: `implementation`
- Problem statement: target repos can now accumulate large agent-facing route
  maps, runtime rules, and prompt adapters. `lint_agent_docs.py` warns on size,
  stale commands, unsafe guidance, and provenance gaps, but there is no compact
  no-write audit that proposes which detail should move into scoped contracts,
  generated reports, scripts, docs, or task packets before pruning happens.
- Background:
  - `AGW-002` and `AGW-004` added agent-instruction linting and bloat checks.
  - `AGW-038` added instruction budgets and hygiene guidance.
  - `AGW-072` made token efficiency a workflow constraint.
  - `AGW-092` added compact context bundles with explicit omissions.
  - The user reported dirty-start and task-start failures on 2026-06-15 and
    asked for kit changes that help agents self-diagnose and close cleanly.
- Non-goals:
  - Do not automatically rewrite or prune `AGENTS.md`, `REVIEW.md`, runtime
    adapters, or prompt files.
  - Do not delete user-authored rules or hide tracked diffs.
  - Do not change the existing `agent-docs-lint` pass/fail behavior unless the
    new audit mode is explicitly requested.
  - Do not make the source repo own installed target-repo instruction files.

## Goal Alignment

- repo_goal: keep `repo-contract-kit` as the install-layer guardrail provider
  for target repos, with deterministic commands that reveal risk and propose
  safe next actions without mutating user work by default.
- area_contracts:
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/lint_agent_docs.py`
    purpose: local agent-instruction analyzer for safety, stale references,
    bloat, provenance, and instruction-hygiene diagnostics.
    source: `docs/ops/agent-instruction-hygiene.md`; installed `agent-docs-lint`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/repo_contract_kit.py`
    purpose: stable kit CLI entrypoint for machine-readable target-repo status
    and agent workflow reports.
    source: `docs/agent-workflow-stack.md`; kit CLI tests
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/`
    purpose: installed target-repo docs, Make targets, and instruction-budget
    defaults.
    source: installer tests; docs freshness checks
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/`
    purpose: operator-facing docs for kit commands, instruction hygiene, and
    rollout behavior.
    source: docs-contract
    status: `aligned`
- alignment_decision: `aligned`
- adaptation_needed: `no`
- stop_conditions:
  - Stop if the implementation would mutate target instruction files instead of
    producing a proposal.
  - Stop if audit recommendations cannot distinguish route-map, duplicated
    procedure, budget pressure, stale command, and offload-target evidence.
  - Stop if JSON output does not give agents enough receipt detail to explain
    why a file is safe, warning, or over budget.

## Scope

- Inspect first:
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/lint_agent_docs.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/repo_contract_kit.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/kit/Makefile.doc-contract-kit`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/docs/ops/agent-instruction-hygiene.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/agent-workflows/instruction-budgets.json`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/test_install.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/test_repo_contract_kit_cli.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/harness-engineering.md`
- Allowed edits:
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/lint_agent_docs.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/repo_contract_kit.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/README.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/VERSION`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/CHANGELOG.md`
  - Source backlog closeout files in `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-workflow-review/` after kit validation passes.
- Protected:
  - User target repos outside the kit checkout.
  - Existing target-owned `VERSION` or `CHANGELOG.md` behavior.
  - Source prompt adapters unless a separate source task is opened.
  - Unrelated backlog rows.
- Expected outputs:
  - A no-write CLI/report mode, exposed through an installed Make target, that
    audits agent-facing instruction files and emits JSON/text recommendations.
  - Recommendation categories for near-budget/over-budget sections, route-map
    violations, duplicated procedural detail, stale or localizable command
    detail, and likely offload targets.
  - Clear recommendation objects with file, line or section evidence, severity,
    reason, and suggested destination such as scoped docs, contracts, generated
    reports, scripts, task packets, or instruction-budget config.
  - Sidecar receipt support only if it follows existing explicit sidecar-write
    patterns; default mode must not mutate the target repo.
  - Docs, tests, version, changelog, and source backlog closeout.

## Coordination

- Active task count: `0` in the source repo before starting AGW-094.
- Active sibling tasks: none reported by `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`.
- Overlap warnings: AGW-094 edits the kit checkout and source closeout metadata
  only after validation. It should not refresh the source repo's installed kit
  layer unless explicitly required for validation.

## Harness Metrics

- Context file count: `8`
- Token budget:
  - Prefer extending the existing instruction-lint analyzer over adding a large
    new parser.
  - Keep text output concise and machine JSON complete; do not copy full file
    contents into audit receipts.

## Acceptance Criteria

- `repo-contract-kit` exposes an instruction-diet audit command or mode, plus
  an installed `make agent-instruction-diet` or equivalent target.
- The audit is no-write by default and produces JSON plus concise text output.
- The report identifies budget pressure, route-map violations, duplicated
  procedural detail, stale/localizable command references, and recommended
  offload destinations with enough evidence for an agent receipt.
- Existing `agent-docs-lint` behavior remains compatible.
- Tests cover CLI output, installed target wiring, no-write behavior, and at
  least one representative recommendation.
- Docs explain when to run the audit and that it proposes pruning rather than
  applying it.
- `VERSION` and `CHANGELOG.md` record the kit behavior change.
- Source backlog rows and summary close `AGW-094` only after kit validation
  passes.

## Validation

- Required commands in `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install tests.test_repo_contract_kit_cli`
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
- Evidence to capture:
  - Focused and full kit test output.
  - Docs/version validation.
  - Source backlog validation.
  - Remote ref match after push.
  - Dirty-state explanation for both checkouts.

## Closeout Requirements

- Final receipt path: `.agent-workflows/tasks/agw-094-instruction-diet-audit/receipt.json` or sidecar equivalent.
- Readiness check:
  - Command: `make agent-task-ready TASK=AGW-094 TASK_READY_JSON=1` or record why unavailable for this parent-run packet.
  - Expected result: ready report passes or blocker is recorded.
- Lifecycle action:
  - Action: `finish`
  - Command: `make agent-task-finish TASK=AGW-094 TASK_RECEIPT=<path> TASK_LIFECYCLE_JSON=1` or lifecycle fallback.
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
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/docs/ops/agent-instruction-hygiene.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/kit/Makefile.doc-contract-kit`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/CHANGELOG.md`
  - source backlog summary files
- Waiver allowed: `no`
- Notes: This adds an installed operator-facing command and report contract.

## Risk And Approval

- Risk level: `medium`
- Known risks:
  - Over-aggressive recommendations could push useful route-map context out of
    startup instructions.
  - Weak heuristics could create noisy reports that agents ignore.
  - If the audit mutates files, it could hide the very evidence operators need
    to review.
  - New command references can break docs freshness if the installed Make target
    is not wired everywhere required.
- Stop conditions:
  - The implementation needs semantic rewriting of instruction files.
  - Tests cannot prove the command is no-write by default.
  - The audit duplicates existing lint output without adding offload proposals.
- Human approval:
  - Approval needed: `no`
  - State: `approved`
  - Approver/notes: User asked to implement the planned workflow-stack backlog
    items serially; AGW-094 is the next open P1 item after AGW-093 publication.

## Handoff

- Recommended prompt: `workflows/prompts/task-packet.md`, then
  `workflows/prompts/verification-sentinel.md`
- Owner: parent agent or one kit worker
