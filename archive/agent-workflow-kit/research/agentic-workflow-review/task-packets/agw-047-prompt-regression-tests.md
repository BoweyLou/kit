# AGW-047 Task Packet: Prompt Regression Tests

## Task

- ID: `AGW-047`
- Title: Add prompt regression tests for persona output schemas and finding quality.
- Priority: `P1`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv`

## Context

- Repository: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Mode: `verification`
- Problem statement: persona review prompts and synthesis prompts require structured, evidence-backed findings, but the repo does not yet have a small deterministic regression suite that proves malformed or low-signal persona outputs are rejected and good examples still pass.
- Background:
  - `agent-workflow-kit` owns canonical prompts under `workflows/prompts/`; `.codex/prompts/` is generated and must stay in sync if prompt sources change.
  - Existing schema work covers the persona manifest, session receipt findings, and review synthesis JSON shape.
  - `scripts/agent_review_run.py` already parses and lightly validates persona and synthesis payloads.
  - `scripts/run_agentic_regression_fixtures.py` checks broader workflow controls, but it does not run golden persona-output examples.
  - `AGW-046` added a pattern for small deterministic benchmark fixtures with text/JSON runner output and focused tests.
- Non-goals:
  - Do not run live LLM/model reviews or add network-dependent evaluation.
  - Do not change reviewer persona missions unless a fixture proves the current prompt text cannot express the expected quality gate.
  - Do not redesign `schemas/review-synthesis.schema.json` or `schemas/session-receipt.schema.json` beyond narrowly required quality fields.
  - Do not change `repo-contract-kit` unless a source-owned fixture exposes an installed-runner bug that the parent thread explicitly integrates.

## Scope

- Inspect first:
  - `workflows/prompts/templates/review-finding.md`
  - `workflows/prompts/review-synthesis.md`
  - `workflows/prompts/personas/manifest.json`
  - `workflows/prompts/personas/*.md`
  - `schemas/session-receipt.schema.json`
  - `schemas/review-synthesis.schema.json`
  - `scripts/agent_review_run.py`
  - `scripts/run_agentic_regression_fixtures.py`
  - `tests/`
  - `research/agentic-regression-research/fixtures/`
  - `research/docs-impact-benchmarks/`
- Allowed edits:
  - a new prompt regression fixture directory under `research/`
  - a deterministic runner under `scripts/`
  - focused tests under `tests/`
  - docs linking the new eval surface from `README.md`, `docs/harness-engineering.md`, or a fixture README
  - `VERSION` and `CHANGELOG.md` when required by version policy
  - canonical prompt files under `workflows/prompts/` only if the regression suite reveals a missing explicit quality requirement
  - generated `.codex/prompts/` adapters only through `make prompt-adapters-export` if canonical prompts change
  - backlog closeout rows and summary after validation passes
- Protected:
  - companion `repo-contract-kit` checkout
  - installed managed-file semantics not owned by this source repo
  - unrelated backlog rows
  - broad schema rewrites or public output contract changes outside this task
  - live review-run artifacts under `.agent-workflows/runs/` unless a local receipt is needed
- Expected outputs:
  - A small fixture suite with named golden examples for valid persona findings, malformed persona payloads, unsupported/nit findings, duplicate findings, and synthesis quality.
  - A deterministic local runner that validates fixture expectations without calling a model or the network.
  - Tests proving that bad examples fail for the intended reason and good examples pass.
  - Documentation showing how to run the suite and what quality signals it protects.

## Coordination

- Active task count: `0`
- Active sibling tasks: none reported by `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1` at packet creation.
- Registered external worktrees: two older automation worktrees exist outside the default sibling pool and are clean; do not modify or clean them from this packet.
- Overlap warnings: none for the primary checkout.

## Harness Metrics

- Context file count: `10`
- Token budget:
  - Prefer fixture-driven tests and existing runner helpers over broad prompt rewrites.
  - Keep golden examples small enough that they are readable in review and cheap to run in `make validate`.

## Acceptance Criteria

- The fixture suite has explicit case ids, intent labels, payload inputs, expected status, and expected validation or quality reasons - verify by reading the fixture file.
- At least one valid persona finding passes with required fields, evidence, recommendation, status, and false-positive notes - verify with runner output and focused tests.
- At least one malformed persona payload fails because required fields or evidence are missing - verify with runner output and focused tests.
- At least one low-signal/nit finding is rejected or downgraded by deterministic quality rules - verify with runner output and focused tests.
- At least one duplicate/overlapping finding example proves synthesis quality expectations such as source-persona preservation or duplicate suppression - verify with runner output and focused tests.
- The runner reuses existing payload validators where possible instead of duplicating schema parsing - verify by reading the runner.
- The benchmark is documented and integrated into local validation if appropriate - verify by reading docs and Make/test changes.
- The backlog row can be closed with evidence from focused tests, prompt adapter checks if prompts changed, and `make agent-verify`.

## Validation

- Required commands:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_prompt_regression_fixtures`
  - `PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_prompt_regression_fixtures.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_prompt_regression_fixtures.py --json`
  - `PYTHONDONTWRITEBYTECODE=1 make prompt-adapters-check` if prompt sources or generated adapters changed
  - `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
  - `git diff --check`
- Evidence to capture:
  - Focused test output.
  - Prompt regression runner text and JSON output.
  - Adapter check output when applicable.
  - Agent verification output.
  - Diff summary and dirty-state explanation.

## Closeout Requirements

- Final receipt path: `.agent-workflows/tasks/agw-047-prompt-regression-tests/receipt.json` or sidecar equivalent.
- Readiness check:
  - Command: `make agent-task-ready TASK=AGW-047 TASK_READY_JSON=1` or record why unavailable for this non-worktree parent-run packet.
  - Expected result: ready report passes or blocker is recorded.
- Lifecycle action:
  - Action: `finish`
  - Command: `make agent-task-finish TASK=AGW-047 TASK_RECEIPT=<path> TASK_LIFECYCLE_JSON=1` or lifecycle fallback.
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
  - prompt regression fixture README or benchmark docs
  - `README.md` or `docs/harness-engineering.md`
  - `CHANGELOG.md`
- Waiver allowed: `no`
- Notes: This adds a new local eval surface and likely a new command.

## Risk And Approval

- Risk level: `medium`
- Known risks:
  - Deterministic quality checks can overfit local wording and reject valid future findings.
  - Too much validation in the runner can duplicate schema ownership or make prompt iteration brittle.
  - Prompt edits require adapter regeneration and can affect installed target repos on the next kit update.
- Stop conditions:
  - The implementation needs live LLM calls or external evaluation services.
  - A required fix belongs in `repo-contract-kit` and cannot be safely integrated in this parent thread.
  - The task grows into a broader review-runner redesign instead of fixture-backed regression checks.
- Human approval:
  - Approval needed: `no`
  - State: `approved`
  - Approver/notes: Active user goal is to implement remaining backlog items serially with one task agent per item.

## Handoff

- Recommended prompt: `workflows/prompts/task-packet.md`, then `workflows/prompts/verification-sentinel.md`
- Owner: one worker agent
- Dependencies:
  - Existing review-finding template, persona manifest, session receipt schema, synthesis schema, and `scripts/agent_review_run.py`.
  - Existing deterministic fixture patterns from AGW-046 and agentic regression fixtures.
- Next packet hint: `AGW-048` should cover review-yield and human-burden metrics separately.
