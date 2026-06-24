# AGW-048 Task Packet: Review Outcome And Burden Metrics

## Task

- ID: `AGW-048`
- Title: Track review yield, false-positive rate, cost/latency,
  time-to-green, and human review burden.
- Priority: `P2`
- Repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv:49`

The harness already carries generic `harness_metrics` and finding
dispositions, but it does not define review-yield, false-positive-rate,
cost/latency, time-to-green, or human-review-burden fields. Without explicit
outcome and effort metrics, the workflow can claim productivity from more
findings or faster generation while hiding reviewer burden, noisy output,
latency, or unmeasured costs.

## Safe Start Evidence

- Source `main` is clean and pushed at
  `774442967cd01d37c6386c159356a5ba01699c49`.
- `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1
  TASK_STATUS_JSON=1` reports zero active tasks, no stale tasks, no hazards, no
  unknown-scope tasks, and no untracked agent worktrees.
- `make agent-next` selects `AGW-048` with `dirty: false`.
- `make backlog-status` reports `8` open and `91` done.
- `make agent-token-budget` reports 104 files and 85776 estimated tokens,
  result `passed`.
- `make kit-status` reports installed `repo-contract-kit` 0.4.41, target repo
  version 0.2.22, runtime adapters `none`, and managed-file drift relative to
  installed kit metadata. Treat that as known self-dogfood drift, not source git
  dirt.

Decision: `safe-start`.

## Implementation Scope

Allowed edits:

- `schemas/session-receipt.schema.json`
- `scripts/verify_agent_receipt.py`
- `scripts/render_session_receipt_summary.py`
- `tests/test_verify_agent_receipt.py`
- `tests/test_render_session_receipt_summary.py`
- `workflows/prompts/review-synthesis.md`
- `workflows/prompts/README.md`
- `.codex/prompts/review-synthesis.md` through `make prompt-adapters-export`
- `.codex/prompts/README.md` through `make prompt-adapters-export`
- `README.md`
- `docs/harness-engineering.md`
- `docs/using-the-prompt-kit.md`
- `VERSION`
- `CHANGELOG.md`
- source backlog closeout files:
  - `research/agentic-workflow-review/backlog.csv`
  - `research/agentic-workflow-review/agent-workflow-kit-backlog.csv`
  - `research/agentic-workflow-review/summary.md`
  - `research/agentic-workflow-review/feature_matrix.csv`

Protected:

- `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/`
- `schemas/task-packet.schema.json` unless a documentation-only reference is
  needed
- `scripts/agent_start.py`
- `scripts/build_context_packet.py`
- `workflows/manifest.json` unless prompt adapter export proves a manifest typo
- `.agent-workflows/` runtime state except deterministic report reads
- metrics storage, dashboards, hosted collectors, CI upload config, or
  account/tool credentials
- unrelated backlog rows and unrelated dirty work

## Inspect First

Read:

- `AGENTS.md`
- `REVIEW.md`
- `.agent-workflows/README.md`
- `schemas/session-receipt.schema.json`
- `scripts/verify_agent_receipt.py`
- `scripts/render_session_receipt_summary.py`
- `tests/test_verify_agent_receipt.py`
- `tests/test_render_session_receipt_summary.py`
- `docs/harness-engineering.md`
- `workflows/prompts/review-synthesis.md`
- `workflows/prompts/README.md`
- `docs/using-the-prompt-kit.md`
- `README.md`

Run or refresh:

- `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
- `make kit-status`

## Expected Shape

Extend optional `harness_metrics` in `schemas/session-receipt.schema.json`.
Keep existing receipts valid when the new fields are absent.

Recommended shape:

- `review_outcome` object:
  - `findings_total`
  - `findings_open`
  - `findings_accepted`
  - `findings_rejected`
  - `findings_fixed`
  - `findings_deferred`
  - `findings_duplicate`
  - `findings_false_positive`
  - `false_positive_rate`
  - `duplicate_rate`
  - `review_yield_count`
  - `review_yield_rate`
  - `human_decision_count`
- `effort` object:
  - `duration_ms`
  - `first_finding_latency_ms`
  - `time_to_green_ms`
  - `commands_run_count`
  - `model_input_tokens`
  - `model_output_tokens`
  - `estimated_cost_usd`
  - `human_review_minutes`
  - `human_interruption_count`
  - optional `notes`

Names can differ if the worker finds a better local pattern, but the fields must
cover review yield, false positives, duplicate/noise, latency, time-to-green,
cost/token effort, and human burden with explicit units and caveats.

Validation requirements:

- counts are non-negative integers
- rates are numbers in the inclusive range `0..1`
- millisecond durations are non-negative integers
- costs are non-negative numbers when present
- optional groups may be omitted
- unknown values must be omitted or represented explicitly as unknown notes, not
  guessed

Update `scripts/render_session_receipt_summary.py` to show a compact Metrics
section when the new metric groups are present. The summary should stay quiet
when the groups are absent.

Update `workflows/prompts/review-synthesis.md` so the Session Receipt section
tells agents to populate review outcome and effort metrics only from actual
findings, dispositions, commands, known timing, and known cost/token data.
Unknown cost, latency, or human-burden values must not be guessed.

Update docs with the key caveat: metrics are calibration evidence, not
productivity proof. Review yield only means accepted/fixed useful findings
relative to emitted findings; it must be interpreted beside severity,
false-positive notes, duplicate rate, human decisions, review time, and
validation quality.

## Non-Goals

- No metrics database, dashboard, hosted telemetry, CI upload, or background
  collector.
- No automatic organization-wide false-positive calculation from git history or
  external systems.
- No mandatory metrics for all existing receipts.
- No repo-contract-kit installed command behavior or target-repo templates.
- No broad reviewer persona rewrite.
- No claim that these metrics prove productivity improvement.

## Acceptance

1. `schemas/session-receipt.schema.json` defines optional review outcome and
   effort metric groups under `harness_metrics` with bounded count/rate/unit
   semantics.
2. `scripts/verify_agent_receipt.py` validates optional metric groups when
   present and keeps receipts without these metrics valid.
3. `scripts/render_session_receipt_summary.py` renders a concise Metrics
   section when review outcome, false-positive, latency, time-to-green, cost, or
   human-burden fields are present.
4. Review synthesis and docs tell agents to capture metrics from actual
   evidence and avoid guessing unknown cost, latency, false-positive, or
   human-burden values.
5. Generated Codex adapters are refreshed if prompt sources changed.
6. The change does not add telemetry collection, dashboards, hosted upload,
   repo-contract-kit behavior, or mandatory metrics for all receipts.
7. Version/changelog and source backlog rows close `AGW-048` only after
   validation passes.

## Required Validation

Run in the source repo:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_verify_agent_receipt tests.test_render_session_receipt_summary`
- `PYTHONDONTWRITEBYTECODE=1 make prompt-adapters-export`
- `PYTHONDONTWRITEBYTECODE=1 make prompt-adapters-check`
- `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
- `PYTHONDONTWRITEBYTECODE=1 make validate`
- `make docs-check`
- `make docs-freshness`
- `python3 scripts/check_doc_impact.py`
- `make version-check`
- `make backlog-check`
- `make backlog-split-check`
- `git diff --check`

Expected version decision: patch bump and changelog entry, because this changes
receipt schema semantics and user-facing review workflow guidance.

Capture:

- schema diff summary for review outcome and effort metric fields
- receipt validator and summary test output
- prompt adapter export/check output if prompts changed
- docs-impact and docs-freshness output
- version/changelog decision
- `git diff --name-only` showing source schema/scripts/tests/docs/prompt/backlog/version
  scope only
- final `git status` and `make agent-task-status` output

## Closeout

- Commit and push source `main`.
- Record or link a final receipt at
  `.agent-workflows/tasks/agw-048-review-outcome-metrics/receipt.json` or a
  durable sidecar equivalent.
- Run or record why unavailable:
  `make agent-task-ready TASK=AGW-048 TASK_READY_JSON=1`.
- Finish any local task metadata with:
  `make agent-task-finalize TASK=AGW-048 TASK_RECEIPT=<path>
  TASK_FINALIZE_JSON=1` or record why unavailable for this parent-run packet.
- Run:
  `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`.
- Preview closeout cleanup if available:
  `make agent-task-closeout TASK=AGW-048 TASK_CLOSEOUT_JSON=1`.
- Final handoff must say whether the source checkout is clean, only expected
  files remain dirty, cleanup is blocked, or unrelated dirt was preserved.
