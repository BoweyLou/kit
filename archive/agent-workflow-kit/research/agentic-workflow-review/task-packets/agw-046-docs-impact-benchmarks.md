# AGW-046 Task Packet: Docs-Impact Benchmark Fixtures

## Task

- ID: `AGW-046`
- Title: Build small benchmark suite for docs-impact false positives/negatives.
- Priority: `P1`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv`

## Context

- Repository: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Mode: `verification`
- Problem statement: docs-impact behavior is tested through implementation unit tests, but there is no small fixture suite that records expected false-positive and false-negative cases before broader automation trusts docs-impact results.
- Background:
  - `AGW-046` is source-owned eval work; `repo-contract-kit` owns the installed docs-impact implementation.
  - The source repo already has an agentic-regression fixture pattern under `research/agentic-regression-research/fixtures/`.
  - `scripts/check_doc_impact.py` is currently kit-managed in this source checkout and should not become source-owned during this packet.
  - `make agent-verify` already runs deterministic regression fixtures for agentic workflow behavior.
- Non-goals:
  - Do not redesign the docs-impact evaluator.
  - Do not add hosted CI, PR comments, or GitHub-specific behavior.
  - Do not implement docs-as-tests or semantic doc/code review from other backlog rows.
  - Do not mutate the companion `repo-contract-kit` checkout unless a fixture exposes a clear evaluator bug and the parent thread explicitly integrates that cross-repo fix.

## Scope

- Inspect first:
  - `scripts/check_doc_impact.py`
  - `doc-contract.json`
  - `research/agentic-regression-research/fixtures/README.md`
  - `research/agentic-regression-research/fixtures/agentic-regression-seed.json`
  - `scripts/run_agentic_regression_fixtures.py`
  - `scripts/validate_agentic_regression_artifacts.py`
  - `tests/`
  - `docs/harness-engineering.md`
- Allowed edits:
  - a new docs-impact benchmark fixture file under `research/`
  - a small deterministic runner under `scripts/`
  - focused unit tests under `tests/`
  - README or fixture docs that explain how to run the benchmark
  - `docs/harness-engineering.md` or `README.md` if needed to link the new eval surface
  - `VERSION` and `CHANGELOG.md` if required by version policy
- Protected:
  - `scripts/check_doc_impact.py` unless a fixture-proven local bug is explicitly fixed and documented
  - companion `repo-contract-kit` checkout
  - unrelated backlog rows
  - generated prompt adapters
  - existing agentic-regression fixture semantics unless intentionally extended
- Expected outputs:
  - A fixture suite with named docs-impact cases and expected pass/fail/category outcomes.
  - At least one expected true positive, one expected false-positive guard, one expected false-negative guard, and one no-docs-needed/waiver case.
  - A deterministic local runner that can run without network or temp repo pollution.
  - Tests that fail if the runner ignores expected outputs or if fixture shape drifts.
  - Docs showing the command and its purpose.

## Coordination

- Active task count: `0`
- Active sibling tasks: none reported by `make agent-task-status` at packet creation.
- Overlap warnings: none.

## Harness Metrics

- Context file count: `8`
- Token budget:
  - Prefer existing fixture and docs-impact scripts over broad repo rereads.

## Acceptance Criteria

- The benchmark fixture suite has explicit case ids, changed files, optional no-docs declarations, expected status, expected categories, and false-positive/false-negative intent - verify by reading the fixture file.
- The runner produces deterministic text or JSON output and exits nonzero when a fixture expectation is violated - verify with a focused test that includes at least one intentionally failing fixture path.
- The runner uses existing docs-impact evaluation logic rather than duplicating matching rules - verify by reading the runner.
- The benchmark is documented in the fixture README, README, or harness docs - verify by reading changed docs.
- The backlog row can be closed with evidence from focused tests and `make agent-verify`.

## Validation

- Required commands:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_impact_benchmarks`
  - `PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_docs_impact_benchmarks.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_docs_impact_benchmarks.py --json`
  - `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
  - `git diff --check`
- Evidence to capture:
  - Focused test output.
  - Benchmark runner output.
  - Agent verification output.
  - Diff summary and dirty-state explanation.

## Closeout Requirements

- Final receipt path: `.agent-workflows/tasks/agw-046-docs-impact-benchmarks/receipt.json` or sidecar equivalent.
- Readiness check:
  - Command: `make agent-task-ready TASK=AGW-046 TASK_READY_JSON=1` or record why unavailable for this non-worktree parent-run packet.
  - Expected result: ready report passes or blocker is recorded.
- Lifecycle action:
  - Action: `finish`
  - Command: `make agent-task-finalize TASK=AGW-046 TASK_RECEIPT=<path> TASK_FINALIZE_JSON=1` or lifecycle fallback.
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
  - fixture README or benchmark docs
  - `README.md` or `docs/harness-engineering.md`
  - `CHANGELOG.md`
- Waiver allowed: `no`
- Notes: This adds a new local eval surface and command.

## Risk And Approval

- Risk level: `medium`
- Known risks:
  - Fixtures can encode current behavior instead of desired behavior.
  - Synthetic cases can overfit implementation details and miss real docs-impact gaps.
  - Changing the kit-managed evaluator in this source repo would break ownership boundaries.
- Stop conditions:
  - A required fix belongs in `repo-contract-kit` and cannot be safely integrated in this parent thread.
  - The benchmark requires network, hosted CI, or external services.
  - The task starts changing docs-impact policy semantics instead of adding fixtures and expected outputs.
- Human approval:
  - Approval needed: `no`
  - State: `approved`
  - Approver/notes: Active user goal is to implement remaining backlog items serially with one task agent per item.

## Handoff

- Recommended prompt: `workflows/prompts/task-packet.md`, then `workflows/prompts/verification-sentinel.md`
- Owner: one worker agent
- Dependencies:
  - Existing docs-impact implementation and `doc-contract.json`.
  - Existing agentic-regression fixture conventions.
- Next packet hint: `AGW-047` should cover prompt regression tests and remain separate.
