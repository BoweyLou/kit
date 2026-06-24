# AGW-029 Task Packet: Codex Review Trace Concept

## Task

- ID: `AGW-029`
- Title: Add `codex-review trace` concept for opening or exporting run evidence.
- Priority: `P2`
- Repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Status: approved
- Source: `research/agentic-workflow-review/backlog.csv:30`

Define the source-side concept for `codex-review trace`: a future interface for
opening or exporting the evidence behind an agent run. This is a docs-first
task. The worker must not implement the CLI or change installed
`repo-contract-kit` command behavior in this slice.

## Safe Start Evidence

- Source main is clean and pushed at
  `0d908ebca9ebb227c0c341363755abc39b6e545d`.
- Kit main is clean and pushed at
  `1a23bb0bb5b3d2f04077ddeacf512b260d9e3221`.
- Source `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1
  TASK_STATUS_JSON=1` reports zero active tasks, no stale tasks, and no
  hazards.
- Source `make agent-next` selects AGW-029 with a clean checkout.
- Source `make agent-token-budget` passes with 97 files and 77458 estimated
  tokens.
- Source `make kit-status` reports installed `repo-contract-kit` 0.4.41 and
  target repo version 0.2.18.

Decision: safe-start.

## Implementation Scope

This is source-side docs/concept work in `agent-workflow-kit`.

Allowed areas:

- `docs/`
- `workflows/prompts/`
- `.codex/prompts/` only if canonical prompts change and adapters are exported
- `schemas/`, `scripts/`, and `tests/` only if a tiny source-side validation
  change is needed to keep the concept precise
- `README.md`, `VERSION`, and `CHANGELOG.md`
- Source backlog closeout files in `research/agentic-workflow-review/` after
  validation passes

Protected areas:

- `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/`
- installed target-repo templates and managed files
- runtime task metadata or sidecar receipts in real target repos
- private transcript content, credentials, account state, cookies, and
  machine-local history outside explicit local evidence paths
- unrelated backlog rows or unrelated dirty work

## Expected Output

The delivered source docs should define:

- what `codex-review trace` means in this stack
- which existing evidence surfaces it composes: session receipts, receipt
  summaries, task packets, context packets, task-status, state-ledger, and
  closeout/finalizer receipts
- why it supports transcript review and debugging without making raw
  transcript export automatic
- local-only and privacy boundaries for transcripts, command output, paths,
  account data, and redaction/omission
- future modes such as inspect/open, export bundle, privacy-redacted handoff,
  and missing-evidence debugging
- a future CLI contract sketch with inputs, outputs, refusal cases, and
  validation expectations, clearly labeled as later work

Do not add a shipped `codex-review trace` command, Make target, hosted service,
GitHub bot, trace database, or remote upload path.

## Acceptance

1. Source docs define the `codex-review trace` concept and clearly mark the CLI
   as future work.
2. The concept composes existing evidence surfaces instead of replacing
   receipts, receipt summaries, context packets, task-status, state-ledger, or
   closeout receipts.
3. Privacy boundaries are explicit: no automatic transcript export, no account
   mutation, no remote upload, and redaction or omission language for sensitive
   content.
4. A future CLI contract sketch names inputs, outputs, refusal cases, and
   validation evidence without claiming current shipped behavior.
5. Prompt guidance or prompt indexes mention trace evidence only if useful for
   debugging or handoff; adapters are regenerated if prompts change.
6. VERSION and CHANGELOG are updated when required by the repo versioning
   contract.
7. Source backlog rows and summary close AGW-029 only after validation passes.

## Required Validation

Run in `agent-workflow-kit`:

- `PYTHONDONTWRITEBYTECODE=1 make prompt-adapters-check`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_render_session_receipt_summary tests.test_export_workflow_adapters tests.test_research_workflow_artifacts`
- `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
- `make validate`
- `make docs-lint`
- `make docs-build`
- `make docs-generate`
- `python3 scripts/check_doc_impact.py`
- `make docs-freshness`
- `make version-check`
- `git diff --check`

After backlog closeout, also run:

- `make backlog-check`
- `make backlog-split-check`

If implementation remains docs-only and a focused test command is narrower than
the three listed unit test modules, record the reason and still run
`agent-verify`, `validate`, docs checks, version check, and whitespace check.

## Closeout

The final handoff must record:

- final receipt path:
  `.agent-workflows/tasks/agw-029-codex-review-trace/receipt.json` or sidecar
  equivalent
- readiness result, or why `agent-task-ready` is unavailable for this
  parent-run packet
- lifecycle/finalizer action, or durable fallback receipt
- final `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
  output summary
- closeout preview state
- dirty-state explanation

Parent owns the task-packet commit, worker launch, integration review,
validation, commit, push, and backlog closeout. Use exactly one worker for this
backlog item.
