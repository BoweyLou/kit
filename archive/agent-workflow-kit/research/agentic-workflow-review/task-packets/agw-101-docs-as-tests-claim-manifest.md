# AGW-101 Task Packet: Docs-As-Tests Claim Manifest

## Task

- ID: `AGW-101`
- Title: Expand docs-as-tests from the OpenAPI prototype into an explicit
  claim-manifest v2.
- Priority: `P1`
- Status: `draft`
- Source: `research/agentic-workflow-review/backlog.csv`

## Context

- Repository: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Mode: `implementation`
- Problem statement: `AGW-030` added an opt-in docs-as-tests prototype for
  manifest-declared OpenAPI method/path assertions. That proves the safety model
  for narrow local checks, but it does not yet give operators a general story
  for selected documentation claims about API schema fields, CLI help, config
  keys, or examples. The next story should define a backward-compatible claim
  manifest that turns explicit docs claims into local evidence without scraping
  prose, executing arbitrary snippets, starting services, or weakening
  docs-impact, docs-freshness, semantic receipt, or doc-code-delta review.
- Background:
  - `AGW-030` shipped the experimental `docs-as-tests` profile outside default
    presets and outside `docs-check`.
  - `AGW-079` added docs-freshness for links, documented Make targets,
    script/schema references, and optional semantic receipts.
  - `AGW-031` kept comment/docstring and semantic doc-code drift in advisory
    review prompts rather than adding a noisy scanner.
  - `AGW-100` is closed in this source checkout at commit `8729b56`; this
    packet is now the selected next backlog item.
  - `make agent-task-status` reported zero active local task metadata before
    this packet was drafted.
- Non-goals:
  - Do not make docs-as-tests part of `make docs-check`, minimal, default, or
    agentic presets by default.
  - Do not scrape prose to infer claims.
  - Do not run arbitrary fenced code blocks or shell commands.
  - Do not start services, use network URLs, mutate target repos, or call hosted
    models.
  - Do not replace semantic doc-code-delta review receipts; this story covers
    explicit executable claims only.
  - Do not re-open the two-repo product surface that `AGW-100` is consolidating.

## Previous Task State (`previous_task_state`)

- report_sources:
  - `make backlog-status`
  - `make agent-next`
  - `make agent-task-status`
  - `git status --short`
- active_tasks:
  - id: `none`
    state: `none`
    evidence: source `make agent-task-status` reported zero active tasks.
- unresolved_blockers:
  - `none; AGW-101 is now the selected next backlog item.`
- dirty_or_stale_state:
  - `The source checkout is dirty with the AGW-101 backlog/story files; keep
    this packet commit separate from implementation and closeout commits.`
- finalizer_receipt_paths:
  - `none for AGW-101; this is a new draft story`
- blocker_receipt_paths:
  - `none`
- allowed_to_start: `yes`
- closeout_required_before_start:
  - decision: `safe-start`
  - reason: `AGW-100 has been closed, AGW-101 is selected by backlog priority,
    and active task status reports no local task metadata.`
  - required_next_step: `Commit this packet, then implement exactly one
    repo-contract-kit worker for AGW-101.`
  - evidence_paths:
    - `research/agentic-workflow-review/backlog.csv`
    - `research/agentic-workflow-review/task-packets/agw-101-docs-as-tests-claim-manifest.md`

## Goal Alignment

- repo_goal: keep `repo-contract-kit` as the normal local guardrail product
  surface for docs contracts, task safety, and workflow-source checks while
  preserving local-only, explicit, non-mutating verification.
- area_contracts:
  - path: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/check_docs_as_tests.py`
    purpose: executable docs-as-tests checker for explicit local assertions.
    source: `AGW-030`, installed docs-as-tests profile
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/profiles/docs-as-tests/`
    purpose: opt-in experimental profile, example manifest, and operator
      guidance.
    source: `AGW-030`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/common/ops-agent-workflow.md`
    purpose: installed operator explanation of docs-freshness, docs-as-tests,
      and semantic receipts.
    source: `docs/ops/agent-workflow.md`
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/repo_contract_kit.py`
    purpose: stable CLI surface for local docs and agent guardrail commands.
    source: installed `repo-contract-kit` CLI
    status: `aligned`
- alignment_decision: `aligned`
- adaptation_needed: `no`
- stop_conditions:
  - Stop if implementation would make docs-as-tests infer claims from prose.
  - Stop if implementation would run arbitrary commands, snippets, services, or
    network calls.
  - Stop if docs-as-tests becomes a default gate without explicit human
    opt-in.
  - Stop if `AGW-100` changes the repo/source layout enough that this packet's
    path assumptions become stale.

## Scope

- Inspect first:
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/check_docs_as_tests.py`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/check_docs_freshness.py`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/repo_contract_kit.py`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/profiles/docs-as-tests/`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/common/ops-agent-workflow.md`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/tests/test_check_docs_as_tests.py`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/tests/test_repo_contract_kit_cli.py`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/tests/test_install.py`
- Allowed edits:
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/check_docs_as_tests.py`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/repo_contract_kit.py`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/profiles/docs-as-tests/`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/common/`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/tests/`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/docs/`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/README.md`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/VERSION`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/CHANGELOG.md`
  - Source backlog closeout files under
    `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-workflow-review/`
    only after kit validation passes.
- Protected:
  - Default/minimal/agentic preset membership.
  - `make docs-check` behavior unless the change is an explicit no-default
    documentation note.
  - Semantic doc-code-delta review prompts and receipts.
  - Real target-repo docs, sidecar receipts, runtime services, network state,
    and unrelated dirty source checkout changes.
- Expected outputs:
  - Backward-compatible docs-as-tests manifest v2 with claim ids, doc source
    paths/anchors, assertion kind, implementation evidence selector,
    safety/confidence tier, owner, tags, and unsupported-claim reporting.
  - Existing OpenAPI method/path assertions continue to pass unchanged.
  - A narrow first implementation slice for at least local OpenAPI schema/status
    assertions plus either explicitly allowlisted read-only CLI/help assertions
    or local config/env-key assertions.
  - JSON/text output that reports passed, failed, skipped, unsupported, and
    refused claims with evidence paths and target_repo_writes/network_used flags.
  - Docs that position docs-as-tests beside docs-impact, docs-freshness,
    semantic receipts, and doc-code-delta review.
  - Focused tests for backward compatibility, new assertion success/failure,
    unsupported claim refusal, unsafe command/network/service refusal, and
    manifest validation errors.

## Coordination

- Active task count: `0` in the source repo before packet creation.
- Active sibling tasks:
  - `none reported by source make agent-task-status`
- Overlap warnings:
  - `Use exactly one repo-contract-kit worker for AGW-101 implementation.`
  - `Keep packet/story, implementation, and source closeout commits separate.`

## Harness Metrics

- Context file count: `source backlog/story files plus selected docs-as-tests
  kit files; do not reread the full workflow stack unless AGW-100 changes the
  path boundary.`
- Deterministic reports:
  - `make backlog-status` selected
    `research/agentic-workflow-review/backlog.csv`.
  - `make agent-next` selected `AGW-101` and reported dirty source state from
    this packet/story slice.
  - `make agent-task-status` reported zero active tasks.
- Token budget:
  - Keep claim manifest docs compact. Prefer examples with three claim kinds
    over long prose about every possible future assertion.

## Acceptance Criteria

- A manifest v2 story exists and is backward compatible with existing
  docs-as-tests manifests from `AGW-030`.
- Every executable claim has an explicit `claim_id`, source documentation
  reference, assertion kind, local evidence selector, safety tier, and expected
  value or predicate.
- The checker refuses unsupported, inferred, network-like, service-starting, or
  write-capable claims with structured reasons rather than guessing.
- At least one richer OpenAPI assertion beyond method/path is implemented, such
  as response status, schema property, required field, or operation id.
- One additional local claim family is implemented only if it can be made safe:
  either explicitly allowlisted read-only CLI/help output checks with timeouts,
  or config/env-key checks against declared local schema/reference files.
- Output distinguishes `passed`, `failed`, `skipped`, `unsupported`, and
  `refused` claims and preserves `target_repo_writes=false` and
  `network_used=false` for safe runs.
- Docs explain when to use docs-as-tests versus docs-freshness, docs-impact,
  semantic receipts, and doc-code-delta reviewer prompts.
- Tests cover compatibility, success/failure, unsafe refusal, unsupported
  claims, malformed manifests, and installed CLI/Make profile behavior.
- `VERSION` and `CHANGELOG.md` record the repo-contract-kit behavior change.
- Source backlog rows and summary close `AGW-101` only after kit validation
  passes.

## Validation

- Required commands in `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_docs_as_tests tests.test_repo_contract_kit_cli tests.test_install`
  - Run any new focused docs-as-tests test module directly if created.
  - `PYTHONDONTWRITEBYTECODE=1 make test`
  - `make docs-check`
  - `make version-check`
  - `git diff --check`
- Required commands in `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview` after
  source closeout:
  - `make backlog-check`
  - `make backlog-split-check`
  - `python3 -m json.tool research/agentic-workflow-review/task-packets/agw-101-docs-as-tests-claim-manifest.json`
  - `git diff --check`

## Closeout Requirements

- Final receipt path:
  `.agent-workflows/tasks/agw-101-docs-as-tests-claim-manifest/receipt.json` or
  sidecar equivalent.
- Readiness check:
  - Command: `make agent-task-ready TASK=AGW-101 TASK_READY_JSON=1` or record
    why unavailable for this parent-run packet.
  - Expected result: ready report passes or blocker is recorded.
- Lifecycle action:
  - Action: `finish`
  - Command: `make agent-task-finalize TASK=AGW-101 TASK_RECEIPT=<path> TASK_FINALIZE_JSON=1`
    or lifecycle fallback.
  - Expected result: metadata is closed and final receipt is linked, or fallback
    receipt is durable.
- Final task status:
  - Command: `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
  - Expected result: task is terminal or no local metadata was created and the
    reason is recorded.
- Closeout preview:
  - Command: `make agent-task-closeout TASK_CLOSEOUT_JSON=1`
  - Expected result: eligible, retained, or blocked cleanup state is recorded.
  - Apply requires explicit approval: `yes`
- Dirty-state explanation:
  - Final handoff must state whether source and kit checkouts are clean, only
    expected files are dirty, cleanup is blocked, or unrelated dirt was
    preserved.

## Documentation Impact

- Expected: `yes`
- Paths:
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/profiles/docs-as-tests/`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/common/ops-agent-workflow.md`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/docs/harness-engineering.md`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/README.md`
  - `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/CHANGELOG.md`
  - source backlog summary files
- Waiver allowed: `no`
- Notes: this changes an opt-in installed docs verification surface and its
  operator story.

## Risk And Approval

- Risk level: `medium`
- Known risks:
  - A broader docs-as-tests surface can become noisy if it infers claims rather
    than requiring explicit manifests.
  - CLI/help assertions can become unsafe if command allowlists, timeouts, and
    write/network refusal are loose.
  - Operators may over-trust executable claims and skip semantic doc-code review
    for claims that cannot be tested locally.
  - `AGW-100` may move source ownership paths before this story is implemented.
- Stop conditions:
  - Implementation requires prose scraping, hosted models, arbitrary shell,
    service startup, network access, or target writes.
  - Existing AGW-030 manifests break.
  - Docs-as-tests is added to default gates without explicit opt-in.
  - The checker cannot clearly distinguish failed, unsupported, skipped, and
    refused claims.
- Human approval:
  - Approval needed: `yes`
  - State: `not-requested`
  - Approver/notes: User approved adding the story to the backlog; implementation
    still needs explicit prioritization after `AGW-100`.

## Handoff

- Recommended prompt: `workflows/prompts/task-packet.md`, then
  `workflows/prompts/tdd/contract-test-design.md` and
  `workflows/prompts/verification-sentinel.md`
- Owner: one repo-contract-kit worker after human prioritization
- Dependencies:
  - `AGW-030` docs-as-tests experimental profile.
  - `AGW-031` doc-code-delta advisory drift labels.
  - `AGW-079` docs-freshness and semantic receipt gate.
  - `AGW-100` workflow-stack consolidation path decisions.
- Next packet hint: after `AGW-100` closeout, use `make agent-next` and decide
  whether `AGW-101` should preempt lower-priority open docs/PR-readiness work.
