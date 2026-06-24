# AGW-051 Task Packet: Local-Model Review-Only Compatibility Notes

## Task

- ID: `AGW-051`
- Title: Add local-model compatibility notes for review-only tasks.
- Priority: `P2`
- Repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv:52`

The stack has local/private review policy, read-only reviewer policy, and
runtime compatibility guidance, but it does not yet say how to decide whether a
local model is appropriate for review-only tasks. Operators need
privacy-oriented guidance without over-claiming local model capability or
confusing community runtimes with supported source adapters.

## Safe Start Evidence

- Source `main` is clean and pushed at
  `db9a064d58843aaca94411aa56ed51d830751867`.
- `make agent-task-status TASK_STATUS_JSON=1` reports zero active tasks, no
  stale tasks, no hazards, no unknown-scope tasks, and no untracked agent
  worktrees.
- `make agent-next` selects `AGW-051` with `dirty: false`.
- `make backlog-status` reports `7` open and `92` done.
- `make agent-token-budget` reports 105 files and 86870 estimated tokens,
  result `passed`.
- `make kit-status` reports installed `repo-contract-kit` 0.4.41, target repo
  version 0.2.23, runtime adapters `none`, and 5 modified managed files
  relative to installed kit metadata. Treat that as known source self-dogfood
  drift, not source git dirt.

Decision: `safe-start`.

## Implementation Scope

Allowed edits:

- `workflows/prompts/policies/local-private-review.md`
- `workflows/prompts/policies/read-only-reviewer-sandbox.md`
- `workflows/prompts/multi-agent-repo-review.md`
- `workflows/prompts/README.md`
- generated `.codex/prompts/` mirrors through `make prompt-adapters-export`
- `docs/runtime-compatibility.md`
- `docs/runtime-adapters.md`
- `docs/using-the-prompt-kit.md`
- `docs/harness-engineering.md`
- `README.md`
- focused tests only if needed for prompt/export invariants
- `VERSION`
- `CHANGELOG.md`
- source backlog closeout files:
  - `research/agentic-workflow-review/backlog.csv`
  - `research/agentic-workflow-review/agent-workflow-kit-backlog.csv`
  - `research/agentic-workflow-review/summary.md`
  - `research/agentic-workflow-review/feature_matrix.csv`

Protected:

- `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/`
- `workflows/manifest.json` unless prompt adapter export proves a manifest typo
- receipt/review schemas
- review runner or adapter exporter scripts
- `.agent-workflows/` runtime state except deterministic report reads
- runtime config files such as `.continue/`, `.goosehints`, `.gooseignore`,
  `.aider.conf.yml`, `.env`, Ollama config, or model caches
- model downloads, benchmark output, hosted telemetry, provider credentials,
  account state, or CI upload configuration
- unrelated backlog rows and unrelated dirty work

## Inspect First

Read:

- `AGENTS.md`
- `REVIEW.md`
- `.agent-workflows/README.md`
- `workflows/prompts/policies/local-private-review.md`
- `workflows/prompts/policies/read-only-reviewer-sandbox.md`
- `workflows/prompts/multi-agent-repo-review.md`
- `docs/runtime-compatibility.md`
- `docs/runtime-adapters.md`
- `docs/using-the-prompt-kit.md`
- `README.md`

Run or refresh:

- `make agent-task-status TASK_STATUS_JSON=1`
- `make kit-status`

If making runtime-specific local-model claims, verify them against current
primary docs and record source URLs plus access dates. At packet creation,
useful primary/current sources included Continue/Ollama docs, Aider/Ollama
docs, Goose provider/Ollama docs, and OpenAI Codex docs for Codex-specific
boundaries. Treat Open Codex forks as community runtimes, not OpenAI Codex
support.

## Expected Shape

Add a local-model suitability section to
`workflows/prompts/policies/local-private-review.md`.

It should say local or self-hosted models can be useful for review-only work
when the task is low risk and privacy-sensitive, such as:

- first-pass documentation/readme scans
- duplicate or low-signal finding triage
- summarizing local diffs or receipt evidence
- checking whether a review needs escalation before sending context to a
  stronger or hosted model

It should also say local models need escalation or human review when the task
involves:

- security, privacy, compliance, legal, medical, financial, credential, or
  account-state risk
- migrations, data deletion, persistence, public APIs, build/release systems,
  or production operations
- large-repo architecture judgments where context limits are likely to hide
  evidence
- weak tool-calling, weak structured-output reliability, stale knowledge, or
  high false-positive/false-negative rates

The policy should distinguish:

- `local-only`: inference and artifacts stay on the machine
- `self-hosted`: endpoint is controlled by the operator but may not be on the
  same machine
- `remote-openai-compatible`: API shape is familiar but data still leaves the
  machine
- `hosted-provider`: repository snippets, diffs, logs, or prompts leave the
  trusted environment
- `unknown`: boundary was not confirmed

Update `docs/runtime-compatibility.md` with local-model notes for review-only
tasks. Keep the support status precise:

- Do not claim generated adapter support unless `agent-workflow-kit` actually
  generates it.
- For runtimes with primary docs for local/Ollama support, cite source URLs and
  access dates.
- For community forks such as Open Codex, separate them from OpenAI Codex
  support.
- For unsupported/unknown surfaces, recommend manual prompt transfer only after
  the operator verifies data boundaries and capability.

Update the review entrypoint or README/docs so operators find the guidance
before choosing a model or provider. Receipt guidance should ask agents to
record the actual data boundary, model/provider expectations, capability
caveats, and escalation decision. Unknown cost, token, latency, or human-burden
values should remain omitted or caveated per AGW-048.

## Non-Goals

- No model installation, runtime configuration, or benchmark run.
- No generated runtime adapters.
- No repo-contract-kit installed behavior.
- No universal model recommendations or hardware recommendations.
- No telemetry, downloads, provider credentials, cloud calls, or CI upload.
- No write-capable implementation-agent policy changes.
- No claim that local models prove privacy, safety, correctness, or
  productivity.

## Acceptance

1. Local/private review policy documents when local models are appropriate for
   review-only tasks and when to escalate to a stronger/human-reviewed path.
2. Runtime compatibility docs include local-model notes that distinguish
   primary-doc-supported local runtimes from manual-only, community, and
   unsupported surfaces without adding generated adapter claims.
3. Guidance tells agents to record actual data boundaries, provider/model
   expectations, capability caveats, and escalation decisions in receipts or
   handoff notes.
4. The implementation does not install models, edit runtime config, add
   repo-contract-kit behavior, add telemetry, or claim local-model productivity
   or security guarantees.
5. Generated Codex adapters are refreshed if canonical prompts or policies
   changed.
6. Version/changelog and source backlog rows close `AGW-051` only after
   validation passes.

## Required Validation

Run in the source repo:

- `PYTHONDONTWRITEBYTECODE=1 make prompt-adapters-export`
- `PYTHONDONTWRITEBYTECODE=1 make prompt-adapters-check`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_export_workflow_adapters`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_prompt_regression_fixtures.py`
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
prompt/docs guidance.

Capture:

- source URLs and access dates used for runtime/local-model claims
- local/private policy diff summary
- runtime compatibility diff summary
- prompt adapter export/check output
- prompt regression or focused test output
- docs-impact and docs-freshness output
- version/changelog decision
- `git diff --name-only` showing source prompt/docs/backlog/version scope only
- final `git status` and `make agent-task-status` output

## Closeout

- Commit and push source `main`.
- Record or link a final receipt at
  `.agent-workflows/tasks/agw-051-local-model-compatibility-notes/receipt.json`
  or a durable sidecar equivalent.
- Run or record why unavailable:
  `make agent-task-ready TASK=AGW-051 TASK_READY_JSON=1`.
- Finish any local task metadata with:
  `make agent-task-finalize TASK=AGW-051 TASK_RECEIPT=<path>
  TASK_FINALIZE_JSON=1` or record why unavailable for this parent-run packet.
- Run:
  `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`.
- Preview closeout cleanup if available:
  `make agent-task-closeout TASK=AGW-051 TASK_CLOSEOUT_JSON=1`.
- Final handoff must say whether the source checkout is clean, only expected
  files remain dirty, cleanup is blocked, or unrelated dirt was preserved.
