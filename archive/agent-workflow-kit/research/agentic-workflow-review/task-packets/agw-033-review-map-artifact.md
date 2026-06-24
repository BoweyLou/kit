# AGW-033 Task Packet: Review-Map Artifact

## Task

- ID: `AGW-033`
- Title: Add review-map artifact for large changesets.
- Priority: `P2`
- Repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Status: approved
- Source: `research/agentic-workflow-review/backlog.csv:34`

Large changesets need a reusable review-map artifact that turns a broad diff
into navigable review clusters, sequence, risk hotspots, and omission notes for
humans and agents. The delivery shape is Markdown/JSON template, so this task
should define the artifact contract rather than shipping a new command.

## Safe Start Evidence

- Source `main` is clean at
  `67476a373b7e4ebe885e125e787f359d44e1468c`.
- `make agent-task-status TASK_STATUS_JSON=1` reports zero active tasks, no
  hazards, no stale tasks, no unknown-scope tasks, and no untracked agent
  worktrees.
- `make agent-next` selects AGW-033 with `dirty: false`.
- `make agent-task-packet-from-backlog BACKLOG_ID=AGW-033` confirms the backlog
  delivery shape is `Markdown/JSON template.`

Decision: safe-start.

## Implementation Scope

Allowed source areas include:

- `workflows/prompts/templates/review-map.md`
- `.codex/prompts/templates/review-map.md`
- `schemas/review-map.schema.json`
- `tests/test_review_map_artifact.py`
- `workflows/prompts/README.md`
- `.codex/prompts/README.md`
- `workflows/manifest.json`
- `.github/copilot-instructions.md`
- `README.md`
- `docs/using-the-prompt-kit.md`
- `docs/harness-engineering.md`
- `docs/codex-review-trace.md`
- backlog, split backlog, summary, feature matrix, `VERSION`, and
  `CHANGELOG.md` for closeout/bookkeeping

Protected:

- `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- repo-contract-kit managed templates and installed target-repo files
- `scripts/build_context_packet.py` unless a focused failing test proves a
  narrow composition bug
- `scripts/agent_review_run.py` and runtime review-runner behavior
- AGW-034 LSP or codegraph lookup surfaces
- AGW-092 installed context-bundle behavior
- unrelated personas, unrelated backlog rows, unrelated task packets, and
  unrelated dirty work

Inspect first:

- `research/agentic-workflow-review/backlog.csv`
- `research/agentic-workflow-review/feature_matrix.csv`
- `research/agentic-workflow-review/source_findings.json`
- `scripts/build_context_packet.py`
- `tests/test_build_context_packet.py`
- `workflows/prompts/templates/task-packet.md`
- `workflows/prompts/templates/review-finding.md`
- `workflows/prompts/README.md`
- `workflows/manifest.json`
- `docs/using-the-prompt-kit.md`
- `docs/harness-engineering.md`
- `docs/codex-review-trace.md`

## Expected Shape

Preferred shape:

- Add `workflows/prompts/templates/review-map.md` as the canonical Markdown
  artifact template.
- Add `schemas/review-map.schema.json` as the machine-readable contract.
- Make the Markdown and JSON surfaces cover:
  - source inputs, including diff range, context packet path, task packet path,
    receipts, and manual inspection notes
  - scope summary and review objective
  - changed-file clusters with rationale, owner or area, changed files,
    supporting context, and uncertainty
  - entrypoints, public contracts, data/schema boundaries, operational
    surfaces, docs, ADRs, scripts, and tests to inspect
  - risk hotspots and reviewer/persona routing
  - recommended review sequence
  - validation and evidence to capture
  - omissions, skipped files, unclassified paths, missing context, and unknowns
  - follow-up task-packet candidates
- Document that review maps compose with `make context-packet` and installed
  context bundles. They should organize evidence, not replace source review.
- Include the template in the existing generated Codex adapter surface.
- Update `workflows/manifest.json` only if needed so review skill users receive
  the template through the existing review prompt surface.
- Add focused tests that validate the schema and check the Markdown template
  names required navigation and omission sections.
- Update docs, version, changelog, feature matrix, summary, and backlog closeout
  after validation.

## Non-Goals

- No new command, Make target, hosted service, GitHub adapter, browser workflow,
  or network behavior.
- No repo-contract-kit or installed target-repo changes.
- No broad changes to `scripts/build_context_packet.py`.
- No AGW-034 LSP/codegraph lookup, semantic call graphing, or cross-language
  symbol indexing.
- No review-runner execution or agent-dispatch changes.
- No private transcript fields in the schema or template.

## Acceptance

1. A reusable Markdown review-map template exists for large changesets and
   guides reviewers through changed-file clusters, entrypoints, contracts, risk
   hotspots, review sequence, validation surfaces, omissions, and follow-up
   packet candidates.
2. A machine-readable review-map JSON schema mirrors the Markdown artifact
   structure without requiring private transcript data or hosted-service fields.
3. The guidance explicitly composes with `make context-packet` or installed
   context bundles and says when direct source, tests, docs, ADRs, scripts,
   runtime config, or receipts must still be inspected.
4. The artifact has explicit omission and uncertainty fields for skipped files,
   unclassified clusters, missing context-packet data, ambiguous ownership, and
   validation gaps.
5. The final diff does not add a CLI, Make target, repo-contract-kit behavior,
   LSP/codegraph lookup, or review-runner mutation.
6. Generated Codex adapters are current and any manifest or skill-pack include
   change is validated.
7. Docs, version, changelog, feature matrix, summary, and backlog closeout
   reflect that AGW-033 shipped a Markdown/JSON artifact contract, not a
   command.

## Required Validation

Run in agent-workflow-kit:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_review_map_artifact`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_export_workflow_adapters`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_export_codex_skill_pack`
  if `workflows/manifest.json` changed; otherwise record not applicable
- `PYTHONDONTWRITEBYTECODE=1 make prompt-adapters-export`
- `PYTHONDONTWRITEBYTECODE=1 make prompt-adapters-check`
- `PYTHONDONTWRITEBYTECODE=1 make validate`
- `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
- `make docs-check`
- `python3 scripts/check_doc_impact.py`
- `make version-check`
- `git diff --check`
- `make backlog-check && make backlog-split-check` after closeout

## Closeout

- Record or link a final receipt at
  `.agent-workflows/tasks/agw-033-review-map-artifact/receipt.json` or a
  durable sidecar equivalent.
- Run or record why unavailable:
  `make agent-task-ready TASK=AGW-033 TASK_READY_JSON=1`.
- Finish any local task metadata with:
  `make agent-task-finalize TASK=AGW-033 TASK_RECEIPT=<path> TASK_FINALIZE_JSON=1`
  or the local lifecycle fallback.
- Final handoff must say whether the checkout is clean, only expected files
  remain dirty, cleanup is blocked, or unrelated dirt was preserved.
