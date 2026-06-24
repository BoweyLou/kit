# AGW-034 Task Packet: LSP Context Lookup Spike

## Task

- ID: `AGW-034`
- Title: Investigate LSP-backed context lookup for local review runner.
- Priority: `P2`
- Repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Status: approved
- Source: `research/agentic-workflow-review/backlog.csv:35`

Definitions and usages can ground large-repo review better than raw file
stuffing, but the local review runner needs a bounded LSP-backed context lookup
design before any command or runner behavior is added. The backlog delivery
shape is `Spike note.`

## Safe Start Evidence

- Source `main` is clean at
  `5565519061b1c59e4518b649fb152553280cd341`.
- `origin/main` matches that commit.
- `make agent-task-status TASK_STATUS_JSON=1` reports zero active tasks, no
  hazards, no stale tasks, no unknown-scope tasks, and no untracked agent
  worktrees.
- `make backlog-status` reports `12` open, `0` partial, `87` done, `99` total.
- `make agent-next` selects AGW-034 with `dirty: false`.
- `make agent-task-packet-from-backlog BACKLOG_ID=AGW-034` confirms the backlog
  delivery shape is `Spike note.`

Decision: safe-start.

## Implementation Scope

Allowed source areas include:

- `research/agentic-workflow-review/spikes/README.md`
- `research/agentic-workflow-review/spikes/agw-034-lsp-context-lookup.md`
- `research/agentic-workflow-review/backlog.csv`
- `research/agentic-workflow-review/agent-workflow-kit-backlog.csv`
- `research/agentic-workflow-review/summary.md`
- `research/agentic-workflow-review/feature_matrix.csv`

Protected:

- `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- repo-contract-kit managed templates and installed target-repo files
- `scripts/agent_review_run.py`
- `scripts/build_context_packet.py`
- `workflows/prompts/`
- `.codex/prompts/`
- `schemas/`
- `tests/`
- `Makefile`
- `VERSION` and `CHANGELOG.md` unless the worker intentionally changes
  user-facing behavior, which this packet does not expect
- unrelated backlog rows, unrelated task packets, and unrelated dirty work

Inspect first:

- `research/agentic-workflow-review/backlog.csv`
- `research/agentic-workflow-review/feature_matrix.csv`
- `research/agentic-workflow-review/source_findings.json`
- `research/agentic-workflow-review/summary.md`
- `research/agentic-workflow-review/task-packets/agw-033-review-map-artifact.md`
- `scripts/agent_review_run.py`
- `scripts/build_context_packet.py`
- `workflows/prompts/templates/review-map.md`
- `schemas/review-map.schema.json`
- `docs/codex-review-trace.md`
- `docs/harness-engineering.md`

## Expected Shape

Preferred shape:

- Add `research/agentic-workflow-review/spikes/agw-034-lsp-context-lookup.md`.
- If the `spikes/` directory is new, add a short `README.md` explaining that
  spike notes capture bounded research, recommendation, stop conditions, and
  follow-on packet shape.
- Ground the note in local source evidence from AGW-032, AGW-033, and the
  current review runner.
- If internet access is used, rely on current primary sources or public source
  repositories and record URLs plus access date in the note.
- Answer build/defer/no-go for LSP-backed lookup.
- Compare at least three approaches:
  - deterministic context packet and review-map fallback only
  - local LSP definition/reference lookup
  - heavier codegraph or search indexing
- Sketch the later architecture:
  - inputs from changed files, context packets, review maps, or task packets
  - outputs such as definitions, references/usages, symbol summaries, files
    inspected, omissions, unsupported-language records, and confidence
  - composition point with `scripts/agent_review_run.py` without mutating it now
  - sidecar/cache policy, token caps, timeout limits, generated/vendor
    exclusions, and local-only privacy boundary
  - failure/refusal behavior for missing language servers, monorepos,
    generated code, unsupported languages, remote-index requests, and
    background daemon requirements
- Include a language/tool availability table covering at least Python,
  TypeScript/JavaScript, Go, Rust, and unknown or unsupported repos, without
  requiring installation during the spike.
- Include a later test plan using fixture repos or golden JSON artifacts.
- Close AGW-034 in the backlog, split backlog, feature matrix, and summary only
  after validation.

## Non-Goals

- No LSP client, codegraph indexer, semantic search service, or review-runner
  integration in AGW-034.
- No command, Make target, installed target-repo schema, repo-contract-kit
  behavior, hosted service, or GitHub/bot integration.
- No auto-installing language servers, package-manager installs, background
  daemons, remote code-indexing services, account credentials, or network
  behavior in shipped repo code.
- No mutation of runner code, context-packet code, prompts, generated adapters,
  schemas, tests, or Make targets.
- No vague closeout. The spike must name recommendation, architecture,
  boundaries, tests, and follow-on backlog shape.

## Acceptance

1. A durable AGW-034 spike note exists and cites local source surfaces plus any
   bounded primary external sources used for the investigation.
2. The spike gives a clear build/defer/no-go recommendation and explains how
   LSP lookup should compose with context packets, review maps, trace evidence,
   and the local read-only review runner.
3. The spike defines later implementation boundaries: local-only, read-only, no
   auto-install, no remote indexing, bounded timeouts, unsupported-language
   behavior, cache/sidecar policy, token caps, and omission reporting.
4. The spike compares deterministic context, local LSP lookup, and heavier
   codegraph/search indexing with concrete pros, cons, and go/no-go triggers.
5. The spike includes a later test plan and follow-on backlog shape instead of
   implementing runner behavior now.
6. Backlog closeout records AGW-034 as a completed spike note and leaves any
   implementation work as explicit follow-on scope.
7. Docs-impact and versioning checks pass with an unchanged-version rationale
   if no behavior, prompt, schema, or user-facing command changed.

## Required Validation

Run in agent-workflow-kit:

- `python3 scripts/check_doc_impact.py`
- `VERSION_CHECK_ALLOW_UNCHANGED=1 make version-check`
- `PYTHONDONTWRITEBYTECODE=1 make validate`
- `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
- `make docs-check`
- `make docs-lint`
- `make docs-build`
- `make docs-generate`
- `git diff --check`
- `make backlog-check && make backlog-split-check`

If the worker changes any code, prompts, schemas, generated adapters, Make
targets, or release-visible behavior, stop and revise the packet before
continuing.

## Closeout

- Record or link a final receipt at
  `.agent-workflows/tasks/agw-034-lsp-context-lookup-spike/receipt.json` or a
  durable sidecar equivalent.
- Run or record why unavailable:
  `make agent-task-ready TASK=AGW-034 TASK_READY_JSON=1`.
- Finish any local task metadata with:
  `make agent-task-finalize TASK=AGW-034 TASK_RECEIPT=<path> TASK_FINALIZE_JSON=1`
  or the local lifecycle fallback.
- Final handoff must say whether the checkout is clean, only expected files
  remain dirty, cleanup is blocked, or unrelated dirt was preserved.
