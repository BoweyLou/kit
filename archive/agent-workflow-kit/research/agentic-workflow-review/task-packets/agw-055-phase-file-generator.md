# AGW-055 Task Packet: Phase-File Generator

## Task

- ID: `AGW-055`
- Title: Add phase-file generator for large reviews and implementations.
- Priority: `P2`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv:56`
- Repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`

## Context

Large reviews and implementations need phase files so fresh agent sessions can
resume a bounded phase without reconstructing the whole plan. This is
agent-workflow-kit source work: edit canonical prompt/template/schema/docs
surfaces first, then regenerate adapters.

Current safe-start evidence:

- `make backlog-status` reports `4` open, `97` done, `0` partial, with
  `AGW-055` selected next.
- `make agent-next` selects `AGW-055` and reports `dirty: false`.
- `make agent-task-status` reports zero active tasks and no coordination
  warnings.
- `make kit-status KIT=/Volumes/Myrtle/Code/04_Code/repo-contract-kit` reports
  installed kit `0.6.2` at `be27b2f` and update current.
- Prior AGW-053 work is committed as repo-contract-kit `be27b2f` and
  Codex_CodeReview `35da7a8`.

Non-goals:

- Do not add a backlog UI, hosted planning service, or external memory adapter.
- Do not implement GitHub, Reddit, BMAD, Keryx, Obsidian, or issue-tracker
  integration in this slice.
- Do not replace the task-packet contract; add phase files as bounded
  continuation artifacts for large work.
- Do not edit repo-contract-kit installed commands unless source adapter sync
  exposes a separately scoped install-layer requirement.

## Goal Alignment

- Repo goal: agent-workflow-kit is the canonical local-first workflow prompt
  source; repo-contract-kit is the install layer.
- Aligned areas:
  - `workflows/prompts/` for canonical task-packet, implementation, and
    verification prompt behavior.
  - `schemas/` if structured phase metadata is needed.
  - `docs/` for operator guidance.
- Decision: `aligned`.
- Stop if the work turns into an installed command, external planning adapter,
  hosted service, or incompatible task-packet schema migration.

## Scope

Inspect first:

- `AGENTS.md`
- `REVIEW.md`
- `.agent-workflows/README.md`
- `workflows/prompts/task-packet.md`
- `workflows/prompts/templates/task-packet.md`
- `schemas/task-packet.schema.json`
- `docs/using-the-prompt-kit.md`
- `docs/working-rhythm.md`
- `tests/test_task_packet_contract.py`
- `tests/test_export_workflow_adapters.py`

Allowed edits:

- `workflows/prompts/task-packet.md`
- `workflows/prompts/templates/task-packet.md`
- `workflows/prompts/fix-planner.md`
- `workflows/prompts/fix-implementer.md`
- `workflows/prompts/verification-sentinel.md`
- `schemas/task-packet.schema.json`
- `docs/using-the-prompt-kit.md`
- `docs/working-rhythm.md`
- `tests/test_task_packet_contract.py`
- `tests/test_export_workflow_adapters.py`
- generated adapters under `.codex/prompts/` and `.github/copilot-instructions.md`
- `VERSION`
- `CHANGELOG.md`
- source closeout files under `research/agentic-workflow-review/`

Protected:

- repo-contract-kit checkout and installed target commands
- runtime credentials, external planning accounts, Keryx/Obsidian vault writes,
  GitHub issues, and hosted PR state
- unrelated `.doc-contract-kit/updates/` proposal artifacts

## Acceptance Criteria

- Task-packet guidance defines when large reviews or implementations should be
  split into phase files.
- Phase files preserve fresh-session continuity without replacing task packets
  or encouraging unbounded mega-plans.
- Implementation and verification prompts can consume phase files when present,
  or the implementation records why no change is needed.
- Generated Codex and Copilot adapters are refreshed after source prompt edits.
- Tests or fixture checks cover the phase-file contract.

## Validation

Run from `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`:

- `make prompt-adapters-export`
- `make prompt-adapters-check`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_task_packet_contract tests.test_export_workflow_adapters`
- `make agent-verify`
- `make docs-check`
- `make version-check`
- `git diff --check`

## Closeout Requirements

- Final receipt path: `.agent-workflows/tasks/AGW-055/receipt.json` or sidecar
  equivalent, or explain why unavailable.
- Readiness: `make agent-task-ready TASK=AGW-055 TASK_READY_JSON=1` or record
  why unavailable.
- Lifecycle: `make agent-task-finalize TASK=AGW-055
  TASK_RECEIPT=.agent-workflows/tasks/AGW-055/receipt.json TASK_FINALIZE_JSON=1`
  or durable fallback receipt.
- Final task status: `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1
  TASK_STATUS_JSON=1`.
- Closeout preview: `make agent-task-closeout TASK_CLOSEOUT_JSON=1`; apply
  requires explicit approval.
- Final handoff must explain dirty state.

## Documentation Impact

Expected: yes.

Required docs/update paths:

- `docs/using-the-prompt-kit.md`
- `docs/working-rhythm.md`
- `CHANGELOG.md`
- `research/agentic-workflow-review/summary.md`

No docs waiver is allowed because this changes prompt/operator behavior.

## Risk And Approval

Risk level: medium.

Known risks:

- Phase files could become a second task-packet format if boundaries are
  unclear.
- Generated adapters can drift if not refreshed.
- Schema changes can break existing packet validation if not backward
  compatible.
- Overly broad phase guidance could encourage large unbounded implementations.

Approval: approved by the user's serial backlog execution request.

Recommended prompt: `workflows/prompts/fix-implementer.md`.

Next packet hint: keep external planning and memory adapter examples separate
for `AGW-059`.
