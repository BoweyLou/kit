# AGW-045 Task Packet: Latest-ADR Discovery And No-ADR Fallback

## Task

- ID: `AGW-045`
- Title: Add latest-ADR discovery guidance and fallback behavior when ADRs do
  not exist.
- Priority: `P2`
- Repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv:46`

The learning-comments prompt already asks agents to inspect latest ADRs, but it
does not define a deterministic ADR discovery order, how to use an agent-start
latest-ADR packet when present, or the fallback behavior when a repository has
no ADRs or decision records. Learning mode depends on design context, so the
prompt should make absence of ADRs explicit without blocking useful
comment-only or explanation-note work.

## Safe Start Evidence

- Source `main` is clean and pushed at
  `e6f75979821811a85565707e12100ffb0613d703`.
- `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1
  TASK_STATUS_JSON=1` reports zero active tasks, no stale tasks, no hazards, no
  unknown-scope tasks, and no untracked agent worktrees.
- `make agent-next` selects `AGW-045` with `dirty: false`.
- `make backlog-status` reports `9` open and `90` done.
- `make agent-token-budget` reports 103 files and 84121 estimated tokens,
  result `passed`.
- `make kit-status` reports installed `repo-contract-kit` 0.4.41, target repo
  version 0.2.21, runtime adapters `none`, and managed-file drift relative to
  installed kit metadata. Treat that as known self-dogfood drift, not source git
  dirt.

Decision: `safe-start`.

## Implementation Scope

Allowed edits:

- `workflows/prompts/codebase-learning-comments.md`
- `.codex/prompts/codebase-learning-comments.md` through
  `make prompt-adapters-export`
- `workflows/prompts/README.md`
- `.codex/prompts/README.md` through generated adapter export if the prompt
  index changes
- `README.md`
- `docs/using-the-prompt-kit.md`
- `tests/test_learning_comments_prompt.py` or a prompt-regression fixture that
  directly checks the new guidance
- `research/prompt-regression-fixtures/prompt-regression-fixtures.json` if using
  fixture coverage
- `VERSION`
- `CHANGELOG.md`
- source backlog closeout files:
  - `research/agentic-workflow-review/backlog.csv`
  - `research/agentic-workflow-review/agent-workflow-kit-backlog.csv`
  - `research/agentic-workflow-review/summary.md`
  - `research/agentic-workflow-review/feature_matrix.csv`

Protected:

- `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/`
- `scripts/agent_start.py`
- `scripts/build_context_packet.py`
- `schemas/session-receipt.schema.json`
- `scripts/verify_agent_receipt.py`
- `docs/adr/`
- `workflows/manifest.json` unless prompt adapter export proves a manifest typo
- `.agent-workflows/` runtime state except deterministic report reads
- generated files other than the Codex prompt adapter mirror
- unrelated backlog rows and unrelated dirty work

## Inspect First

Read:

- `AGENTS.md`
- `REVIEW.md`
- `.agent-workflows/README.md`
- `workflows/prompts/codebase-learning-comments.md`
- `workflows/prompts/README.md`
- `docs/using-the-prompt-kit.md`
- `README.md`
- `scripts/agent_start.py` for existing `latest_adr` and no-ADR warning
  behavior
- `scripts/build_context_packet.py` for existing ADR bucket behavior
- `tests/test_export_workflow_adapters.py`
- `tests/test_prompt_regression_fixtures.py`
- `research/prompt-regression-fixtures/prompt-regression-fixtures.json`

Run or refresh:

- `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
- `make kit-status`

## Expected Shape

Update `workflows/prompts/codebase-learning-comments.md` so learning-comments
mode says:

- Start ADR discovery from deterministic reports already available to the
  session:
  - `make agent-start` or session-start packet latest ADR field
  - context packet or context bundle ADR items
  - explicit task packet, backlog row, issue, or operator-provided decision
    references
- If those reports do not provide a decision source, scan compact known
  locations such as `docs/adr/`, `docs/adrs/`, `adr/`, `adrs/`, and obvious
  architecture/decision docs before reading broadly.
- Treat the latest/current ADR as a constraint/default, and record superseded
  or conflicting decisions as uncertainty rather than silently choosing one.
- When no ADR or ADR-like decision record exists:
  - record `No ADR or decision record found` as evidence;
  - fall back to README, docs, tests, code, config, changelog, issue/task
    context, and operator instructions;
  - do not fabricate design intent or product rationale;
  - add comments only for claims supported by fallback evidence;
  - use a separate explanation note when design context is missing but useful
    code-path explanation can still be evidence-backed;
  - mark unresolved architecture or terminology questions as uncertainty.
- ADR Reader output must report:
  - files inspected;
  - latest/current decision source, if any;
  - superseded or conflicting decisions, if any;
  - no-ADR fallback evidence used;
  - claims that must stay out of comments because they are unsupported.
- Verification must check terminology and design claims against latest decisions
  when present, or against fallback docs/code evidence when absent.

Update prompt docs/indexes with a short discoverability note. Do not duplicate
the whole prompt.

Add focused regression coverage. A small `tests/test_learning_comments_prompt.py`
that asserts the canonical prompt includes ADR discovery order, no-ADR fallback,
unsupported-claim uncertainty, and generated adapter parity is acceptable. A
prompt-regression fixture is also acceptable if it checks the same contract.

## Non-Goals

- No ADR parser or startup/context packet implementation changes.
- No real ADR file changes.
- No automated stale-comment scanner.
- No session receipt schema or strict validator changes.
- No repo-contract-kit changes.
- No behavior, dependency, generated-docs infrastructure, release tag, PR, or
  hosted automation changes.
- No permission for agents to invent architecture decisions, infer product
  intent as fact, or block learning work only because no ADR exists.

## Acceptance

1. `workflows/prompts/codebase-learning-comments.md` defines deterministic ADR
   discovery, starting from existing agent-start/context evidence when present
   and then scanning documented ADR-like locations.
2. The prompt defines no-ADR fallback behavior: record no ADR found, use other
   source-of-truth docs/tests/code evidence, preserve uncertainty, avoid
   fabricated design intent, and continue only with evidence-backed comments or
   explanation notes.
3. ADR Reader and output sections require latest/current/superseded decisions,
   source files, no-ADR fallback evidence, and uncertainty.
4. Docs/index surfaces mention the fallback briefly.
5. Generated `.codex/prompts/codebase-learning-comments.md` mirrors the
   canonical prompt.
6. The change does not alter startup/context packet behavior, receipt schema,
   strict receipt validation, repo-contract-kit files, or actual ADR records.
7. Version/changelog and source backlog rows close `AGW-045` only after
   validation passes.

## Required Validation

Run in the source repo:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_learning_comments_prompt`
  if a focused prompt text test is added; otherwise record why the
  prompt-regression fixture covers this instead
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_prompt_regression_fixtures.py`
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
a user-facing prompt workflow and generated Codex adapter.

Capture:

- prompt diff summary showing ADR discovery and no-ADR fallback sections
- generated adapter check output
- focused test or prompt-regression output
- docs-impact and docs-freshness output
- version/changelog decision
- `git diff --name-only` showing source prompt/docs/test/backlog/version scope
  only
- final `git status` and `make agent-task-status` output

## Closeout

- Commit and push source `main`.
- Record or link a final receipt at
  `.agent-workflows/tasks/agw-045-latest-adr-learning-fallback/receipt.json` or
  a durable sidecar equivalent.
- Run or record why unavailable:
  `make agent-task-ready TASK=AGW-045 TASK_READY_JSON=1`.
- Finish any local task metadata with:
  `make agent-task-finalize TASK=AGW-045 TASK_RECEIPT=<path>
  TASK_FINALIZE_JSON=1` or record why unavailable for this parent-run packet.
- Run:
  `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`.
- Preview closeout cleanup if available:
  `make agent-task-closeout TASK=AGW-045 TASK_CLOSEOUT_JSON=1`.
- Final handoff must say whether the source checkout is clean, only expected
  files remain dirty, cleanup is blocked, or unrelated dirt was preserved.
