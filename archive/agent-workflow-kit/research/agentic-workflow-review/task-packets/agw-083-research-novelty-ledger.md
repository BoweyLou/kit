# AGW-083 Task Packet: Research Novelty Ledger

## Task

- ID: `AGW-083`
- Title: Add a research novelty ledger and candidate-idea scoring to recurring backlog loops.
- Priority: `P1`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv`

## Context

- Repository: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Mode: `verification`
- Problem statement: recurring research/backlog loops can repeat prior questions and rediscover the same runtime-export or meta-cleanup topics because research briefs and syntheses do not carry prior-question fingerprints, candidate scoring, novelty thresholds, or rejected/deferred carry-forward state.
- Background:
  - `AGW-062` added the targeted research workflow with research briefs, source reports, synthesis, and handoff prompts.
  - `AGW-082` added automation-safe branch-or-patch handoff in `repo-contract-kit`; this packet is the source-side prompt/schema layer for deciding what is novel enough to propose before a handoff exists.
  - `schemas/research-brief.schema.json` and `schemas/research-synthesis.schema.json` define the current artifact contracts.
  - `scripts/agent_research.py` emits template artifacts used by local research runs.
  - Canonical prompt edits start under `workflows/prompts/research/`; `.codex/prompts/research/` is generated and must be refreshed through `make prompt-adapters-export`.
- Non-goals:
  - Do not implement automation scheduling, GitHub posting, or hosted CI behavior.
  - Do not mutate recurring automation configuration or outside-repo memory stores.
  - Do not make source agents write backlog rows directly; research still produces proposals until a human or approved handoff accepts writes.
  - Do not create a generalized ranking engine beyond deterministic artifact fields, prompts, and template/test coverage.

## Scope

- Inspect first:
  - `workflows/prompts/research/README.md`
  - `workflows/prompts/research/research-brief.md`
  - `workflows/prompts/research/research-synthesis.md`
  - `workflows/prompts/research/research-to-backlog.md`
  - `schemas/research-brief.schema.json`
  - `schemas/research-synthesis.schema.json`
  - `schemas/research-source-report.schema.json`
  - `scripts/agent_research.py`
  - `tests/test_research_workflow_artifacts.py`
  - `docs/harness-engineering.md`
  - `docs/working-rhythm.md`
- Allowed edits:
  - research prompt sources under `workflows/prompts/research/`
  - generated Codex adapters under `.codex/prompts/research/` via `make prompt-adapters-export`
  - research schemas under `schemas/`
  - `scripts/agent_research.py`
  - focused tests under `tests/`
  - docs that explain the novelty/carry-forward contract
  - `VERSION` and `CHANGELOG.md`
  - backlog closeout rows and summary after validation passes
- Protected:
  - companion `repo-contract-kit` checkout
  - unrelated prompt families outside `workflows/prompts/research/`
  - recurring automation config outside this repo
  - source report semantics unless necessary to carry novelty source evidence
  - unrelated backlog rows
- Expected outputs:
  - Research brief artifacts can declare prior-question fingerprints, known recent topics, novelty threshold, and carry-forward rejected/deferred leads.
  - Research synthesis artifacts can score candidate ideas for novelty, evidence strength, fit, effort, risk, and recommendation state.
  - Prompts instruct recurring research loops to compare against the ledger, score several candidates, reject low-novelty repeats, and carry forward rejected/deferred leads before proposing backlog edits.
  - `scripts/agent_research.py` templates include the new fields.
  - Focused tests prove the schemas, prompts, and generated templates include the new contract.

## Coordination

- Active task count: `0`
- Active sibling tasks: none reported by `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1` at packet creation.
- Registered external worktrees: two older automation worktrees exist outside the default sibling pool and are clean; do not modify or clean them from this packet.
- Overlap warnings: none for the primary checkout.

## Harness Metrics

- Context file count: `10`
- Token budget:
  - Keep schema additions compact and avoid embedding long research histories in prompts.
  - Prefer fields that reference prior fingerprints and carry-forward summaries over copying full prior transcripts into each research run.

## Acceptance Criteria

- `schemas/research-brief.schema.json` includes a bounded novelty/carry-forward object with prior-question fingerprints or recent-topic summaries, a novelty threshold, and rejected/deferred lead carry-forward fields - verify by reading the schema and tests.
- `schemas/research-synthesis.schema.json` includes candidate scoring fields for novelty, evidence strength, fit, effort, risk, recommendation state, and rationale - verify by reading the schema and tests.
- `scripts/agent_research.py plan` and `synthesize` templates emit valid default novelty ledger and candidate-score structures - verify with focused tests or generated template inspection.
- Research prompts require recurring loops to review the novelty ledger before proposing backlog changes, score multiple candidate ideas, reject low-novelty repeats, and carry forward rejected/deferred leads - verify by reading prompt sources and generated adapters.
- `make prompt-adapters-export` is run after prompt edits and `make prompt-adapters-check` passes - verify command output.
- Docs mention the novelty/carry-forward contract where operators understand recurring research behavior - verify changed docs.
- The backlog row can be closed with evidence from focused tests, adapter checks, and `make agent-verify`.

## Validation

- Required commands:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_research_workflow_artifacts`
  - `PYTHONDONTWRITEBYTECODE=1 make prompt-adapters-check`
  - `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
  - `make backlog-check`
  - `make backlog-split-check`
  - `git diff --check`
- Evidence to capture:
  - Focused research workflow test output.
  - Prompt adapter export/check output.
  - Agent verification output.
  - Backlog status after closeout.
  - Diff summary and dirty-state explanation.

## Closeout Requirements

- Final receipt path: `.agent-workflows/tasks/agw-083-research-novelty-ledger/receipt.json` or sidecar equivalent.
- Readiness check:
  - Command: `make agent-task-ready TASK=AGW-083 TASK_READY_JSON=1` or record why unavailable for this non-worktree parent-run packet.
  - Expected result: ready report passes or blocker is recorded.
- Lifecycle action:
  - Action: `finish`
  - Command: `make agent-task-finish TASK=AGW-083 TASK_RECEIPT=<path> TASK_LIFECYCLE_JSON=1` or lifecycle fallback.
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
  - `workflows/prompts/research/README.md`
  - `docs/harness-engineering.md` or `docs/working-rhythm.md`
  - `CHANGELOG.md`
- Waiver allowed: `no`
- Notes: This changes research artifact contracts, prompt behavior, and template output.

## Risk And Approval

- Risk level: `medium`
- Known risks:
  - Overly rigid scoring can suppress genuinely useful follow-up work.
  - Schema changes affect downstream generated adapters and installed prompt consumers.
  - Novelty fields can become performative if prompts do not force low-novelty rejection and carry-forward.
- Stop conditions:
  - The implementation requires writing to Obsidian/Keryx memory or recurring automation config.
  - The task expands into automation scheduling or backlog mutation authority.
  - Prompt adapter generation produces unexpected changes outside the research prompt family.
- Human approval:
  - Approval needed: `no`
  - State: `approved`
  - Approver/notes: Active user goal is to implement remaining backlog items serially with one task agent per item.

## Handoff

- Recommended prompt: `workflows/prompts/task-packet.md`, then `workflows/prompts/verification-sentinel.md`
- Owner: one worker agent
- Dependencies:
  - Existing targeted research prompt/schema stack from `AGW-062`.
  - Existing automation-safe handoff boundary from `AGW-082`.
- Next packet hint: `AGW-048` can separately add review-yield, false-positive, cost/latency, and human-burden metrics.
