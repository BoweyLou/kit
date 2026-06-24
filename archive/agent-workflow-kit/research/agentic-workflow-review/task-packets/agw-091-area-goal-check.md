# AGW-091 Task Packet: Area Goal Check

## Task

- ID: `AGW-091`
- Title: Add deterministic area-contract discovery and goal-check reporting for changed paths.
- Priority: `P1`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv`

## Context

- Repository: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- Mode: `verification`
- Problem statement: installed target repos now have a source-side task-packet goal-alignment contract from `AGW-090`, but agents still have to reread broad docs manually to decide which repo or folder purpose a changed file should align with. The kit needs a cheap deterministic report that maps changed files to declared area contracts and exposes aligned, extension, conflict, and unknown states.
- Background:
  - `AGW-090` added required `goal_alignment` fields to source task packets.
  - `repo-contract-kit` owns installed commands, target-repo scripts, managed templates, and Make targets.
  - `scripts/repo_contract_kit.py` already has read-only CLI report patterns for `status`, `doc-impact`, `agent-preflight`, `task-packet`, and backlog operations.
  - `scripts/agent_start.py` and `scripts/agent_task_ready.py` already collect changed files for startup and handoff gates.
  - Installed prompt/schema snapshots under `templates/profiles/review-prompts/` and `templates/common/task-packet.schema.json` may need refresh so generated task packets can carry the `AGW-090` goal-alignment contract.
- Non-goals:
  - Do not build a planning app, hosted service, or semantic code ownership database.
  - Do not make `AGENTS.md` the place for detailed area rules; use a structured installed config/template.
  - Do not require target repos to have perfect area contracts on first run; report `unknown` explicitly.
  - Do not change source prompt wording in `agent-workflow-kit` beyond backlog closeout evidence for this implemented kit item.

## Goal Alignment

- repo_goal: keep `repo-contract-kit` responsible for installed target-repo
  execution surfaces that make `agent-workflow-kit` contracts usable without
  broad manual rereads.
- area_contracts:
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/`
    purpose: installed CLI and target-repo scripts that emit deterministic
    harness reports.
    source: `docs/agent-workflow-stack.md`; `docs/harness-engineering.md`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/`
    purpose: managed target-repo templates for Make targets, schemas, docs, and
    local agent workflow config.
    source: `scripts/install.py`; `docs/repo-boundary.md`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/`
    purpose: regression coverage for installed CLI, installer, startup, and
    readiness behavior.
    source: `Makefile`; existing test modules
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-workflow-review/`
    purpose: source-side backlog and packet records for cross-repo workflow
    stack work.
    source: `docs/agent-workflow-stack.md`
    status: `aligned`
- alignment_decision: `aligned`
- adaptation_needed: `no`
- stop_conditions:
  - Stop if implementation requires changing canonical prompt source in
    `agent-workflow-kit` rather than vendored install snapshots.
  - Stop if the proposed report needs external services, hosted CI, or semantic
    LLM classification to work.
  - Stop if generated task-packet scaffolds cannot remain valid when area
    contracts are missing; missing contracts must report `unknown`.

## Scope

- Inspect first:
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/repo_contract_kit.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_start.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/agent_task_ready.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/install.py`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/kit-makefile.mk`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/task-packet.schema.json`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/profiles/review-prompts/files/.codex/prompts/task-packet.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/profiles/review-prompts/files/.codex/prompts/templates/task-packet.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/harness-engineering.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/rollout-guide.md`
- Allowed edits:
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/scripts/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/profiles/review-prompts/files/.codex/prompts/` only to refresh installed task-packet prompt/schema snapshot behavior
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/tests/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/README.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/VERSION`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/CHANGELOG.md`
  - Source backlog closeout files in `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-workflow-review/` after the kit change is validated.
- Protected:
  - Canonical source prompt files under `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/workflows/prompts/`
  - Source repo `AGENTS.md`, `REVIEW.md`, and `.agent-workflows/` state
  - Existing target-repo customization semantics in update/install flows
  - Hosted GitHub Actions behavior unless only docs mention the local report
  - Unrelated backlog rows
- Expected outputs:
  - A structured area-contract config/template, preferably under `.agent-workflows/`, with repo goal plus path contracts containing purpose/owner/validation/status or similar deterministic fields.
  - A CLI report, preferably `repo_contract_kit.py goal-check`, that accepts explicit changed files or uses working-tree/staged/branch modes, maps paths to area contracts, and emits text and JSON.
  - A Make target such as `make goal-check` or `make area-check` in installed repos.
  - Report states distinguish at least `aligned`, `extends`, `conflict`, and `unknown`, with unknowns treated as visible warnings rather than guessed alignment.
  - `agent-start` includes or references the current goal-check report for changed files.
  - Task-packet scaffolds include goal-alignment defaults populated from the report when available.
  - `agent-task-ready` reports goal-check status for actual changed files without replacing its existing scope/receipt/freshness gates.
  - Tests cover config loading, path matching precedence, unknown paths, CLI JSON/text output, Make/installer integration, startup packet integration, and readiness integration.

## Coordination

- Active task count: `0` in the source repo after AGW-090 publication.
- Active sibling tasks: none reported by `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`.
- Overlap warnings: this task edits the companion kit checkout plus source backlog records; keep commits separate by repo.

## Harness Metrics

- Context file count: `11`
- Token budget:
  - Prefer a compact deterministic report over copying broad docs into every startup or task packet.
  - Config should summarize area purposes and validation commands, not embed long runbooks.

## Acceptance Criteria

- Installed repos can define area contracts in a structured local file and the kit installs a useful default/example without making unknown target areas fail adoption - verify by installer tests and file inspection.
- `repo_contract_kit.py goal-check` or equivalent emits JSON and text mapping changed files to area contracts, including aligned, extends, conflict, and unknown states - verify with CLI tests.
- The installed Make target exposes the report and is documented in workflow help/operator docs - verify install/Make tests and docs.
- `agent-start` packets include a goal-check or area-goal summary for current changed files - verify `tests/test_agent_start.py` or equivalent.
- `agent-task-ready` includes goal-check status for the task worktree's actual changed files and warns/blocks according to the accepted design without weakening existing readiness blockers - verify `tests/test_agent_task_ready.py`.
- Task-packet scaffolds include valid `goal_alignment` fields that can be populated from the deterministic report or explicit unknowns - verify CLI tests and installed task-packet schema/prompt snapshots.
- `VERSION` and `CHANGELOG.md` in `repo-contract-kit` record the new installed behavior.
- Source backlog rows and summary close `AGW-091` only after kit validation passes.

## Validation

- Required commands in `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_repo_contract_kit_cli`
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_agent_start tests.test_agent_task_ready tests.test_install`
  - `PYTHONDONTWRITEBYTECODE=1 make test`
  - `make docs-check`
  - `make version-check`
  - `git diff --check`
- Required commands in `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview` after source backlog closeout:
  - `make backlog-check`
  - `make backlog-split-check`
  - `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
  - `git diff --check`
- Evidence to capture:
  - Focused CLI/start/readiness/install test output.
  - Full kit test/docs/version output.
  - Source backlog check and agent-verify output after closeout.
  - Diff summary for both repos.
  - Dirty-state explanation for both repos.

## Closeout Requirements

- Final receipt path: `.agent-workflows/tasks/agw-091-area-goal-check/receipt.json` or sidecar equivalent.
- Readiness check:
  - Command: `make agent-task-ready TASK=AGW-091 TASK_READY_JSON=1` or record why unavailable for this non-worktree parent-run packet.
  - Expected result: ready report passes or blocker is recorded.
- Lifecycle action:
  - Action: `finish`
  - Command: `make agent-task-finish TASK=AGW-091 TASK_RECEIPT=<path> TASK_LIFECYCLE_JSON=1` or lifecycle fallback.
  - Expected result: metadata is closed and final receipt is linked, or fallback receipt is durable.
- Final task status:
  - Command: `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
  - Expected result: task is terminal or no local metadata was created and the reason is recorded.
- Closeout preview:
  - Command: `make agent-task-closeout TASK_CLOSEOUT_JSON=1`
  - Expected result: eligible, retained, or blocked cleanup state is recorded.
  - Apply requires explicit approval: `yes`
- Dirty-state explanation:
  - Final handoff must say whether each checkout is clean, only expected files are dirty, cleanup is blocked, or unrelated dirt was preserved.

## Documentation Impact

- Expected: `yes`
- Paths:
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/README.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/harness-engineering.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/docs/rollout-guide.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/working-rhythm.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/templates/common/ops-agent-workflow.md`
  - `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/CHANGELOG.md`
  - source backlog summary files
- Waiver allowed: `no`
- Notes: This adds installed CLI/Make behavior and a managed target-repo contract file.

## Risk And Approval

- Risk level: `medium`
- Known risks:
  - Path matching can give false confidence if broad globs shadow specific area contracts.
  - Blocking unknown areas too early could stop useful adoption in repos without area contracts; unknowns should be visible and configurable.
  - Task-packet schema/prompt snapshots in the kit can drift from the source `AGW-090` contract if only the CLI is updated.
  - Integrating with readiness must not weaken existing scope drift, receipt, docs-impact, freshness, or overlap gates.
- Stop conditions:
  - The implementation requires semantic LLM classification instead of deterministic path/config matching.
  - The work expands into `AGW-092` compact context bundles or `AGW-095` dirty-primary baselines.
  - Updating installed task-packet prompt/schema snapshots requires unreviewed source prompt changes rather than consuming the already-published `AGW-090` state.
- Human approval:
  - Approval needed: `no`
  - State: `approved`
  - Approver/notes: Active user goal is to implement remaining backlog items serially with one task agent per item.

## Handoff

- Recommended prompt: `workflows/prompts/task-packet.md`, then `workflows/prompts/verification-sentinel.md`
- Owner: one worker agent
- Dependencies:
  - `AGW-090` source-side task-packet goal-alignment contract.
  - Existing kit path classification and changed-file helpers in `check_doc_impact.py`, `repo_contract_kit.py`, `agent_start.py`, and `agent_task_ready.py`.
- Next packet hint: `AGW-092` should compose this report into a compact context bundle with other deterministic startup and handoff signals.
