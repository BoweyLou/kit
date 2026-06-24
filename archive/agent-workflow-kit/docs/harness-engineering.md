# Harness Engineering

Use this page when the workflow stack starts to look like a collection of
separate commands. The stack is an agent harness: it shapes what agents see,
what tools they can use, where they write, how evidence is captured, and how a
human decides whether the work is trustworthy.

This is now a legacy source-side design note. It names harness components and
quality gates that should continue under `repo-contract-kit/workflows/` and the
`repo-contract-kit` installer surface.

## Definition

Harness engineering is the design of the environment around an agent, not only
the prompt inside the agent. In this repo family, the harness includes:

- startup, context packets, and review maps
- prompt and schema source
- permission and trust profiles
- task packets and isolated worktrees
- source-specific research artifacts
- receipts and summaries
- trace evidence maps
- docs, version, and regression gates
- backlog and task handoff rules

The practical goal is not more ceremony. The goal is a repeatable workflow where
an agent can start with the right context, stay inside the right boundaries,
produce audit evidence, and stop before unapproved mutation.

## Component Map

| Component | Owner | Lifecycle stage | Current artifact | Evidence produced | Failure mode guarded |
| --- | --- | --- | --- | --- | --- |
| Stack map | `repo-contract-kit` plus legacy source history | orient | `docs/agent-workflow-stack.md` | repo ownership and routing rule | edits landing in the wrong repo |
| Working rhythm | `repo-contract-kit` | orient | `docs/working-rhythm.md` | command sequence for orient, review, scope, execute | command sprawl and unclear next step |
| Startup packet | `repo-contract-kit` install layer | orient | `make agent-start`, `.agent-workflows/runs/*` | changed files, docs impact, ADR context, kit/version state, receipt template | stale context and unaudited session start |
| Next-work surface | `repo-contract-kit` install layer | orient | `make agent-next` | selected backlog source, next open item, dirty state, active tasks | returning agents choosing work from stale memory |
| Context bundle | `repo-contract-kit` install layer | orient and handoff | installed `agent-context-bundle` target | bounded startup, backlog, task, docs-impact, goal, token-budget, readiness, sidecar, and omission summary | broad repo rereads and hidden missing context |
| Backlog contract | `repo-contract-kit` install layer | orient and scope | `make backlog-status`, `make backlog-check`, `make agent-task-packet-from-backlog` | source/mirror health, duplicate ids, portable task-packet scaffold | backlog shape drift and unscoped handoffs |
| Context packet | legacy source history; installed successor belongs in `repo-contract-kit` | review and scope | `scripts/build_context_packet.py`, `make context-packet` | changed files, likely callers, tests, docs, ADRs, scripts, runtime configs | generic review without local grounding |
| Review map | `repo-contract-kit/workflows/` | review and handoff | `workflows/prompts/templates/review-map.md`, `schemas/review-map.schema.json` | changed-file clusters, entrypoints, contracts, risk hotspots, review sequence, validation evidence, omissions, follow-up task-packet candidates | broad changesets hiding uninspected paths or missing context |
| Goal check | `repo-contract-kit` install layer | scope and verify | installed `goal-check` target | changed-path area-contract status, goal alignment, conflicts, unknowns, and stop signals | agents rereading broad docs or inventing area purpose |
| Prompt source and adapters | `repo-contract-kit/workflows/` | review and execute | `workflows/prompts/`, `.codex/prompts/`, `.github/copilot-instructions.md`, `workflows/manifest.json` | adapter sync check and generated prompt projection | prompt drift across runtimes |
| Permission profiles | `repo-contract-kit` install layer | review and execute | `.agent-workflows/agent-permission-policy.json` | selected trust profile and allowed surfaces | read-only agents mutating files or accounts |
| Targeted research | `repo-contract-kit/workflows/` for prompts; installer execution in `repo-contract-kit` | review and scope | `workflows/prompts/research/`, `scripts/agent_research.py` | research brief, novelty ledger, source reports, scored candidate ideas, synthesis, handoff prompt | broad random research, weak evidence, or repeated low-novelty ideas entering backlog |
| Task packet | `repo-contract-kit/workflows/` | scope | `workflows/prompts/task-packet.md`, `schemas/task-packet.schema.json` | previous task state, closeout-before-start decision, repo goal, area contracts, alignment decision, allowed files, protected files, validation, closeout requirements, docs impact, risk, approval | broad human request becoming unbounded edits, goal drift, starting on unresolved prior work, or unfinished cleanup |
| Task status | `repo-contract-kit` | execute | `make agent-task-status` | active scopes, worktree registry, coordination warnings | parallel agents colliding invisibly |
| Task worktree | `repo-contract-kit` | execute | `make agent-task-prepare` | branch, sibling worktree, task packet, receipt template, in-flight metadata | write-capable agent editing the main checkout |
| Task lifecycle | `repo-contract-kit` | execute and handoff | `make agent-task-heartbeat`, `make agent-task-finish`, `make agent-task-block`, `make agent-task-abandon`, `make agent-task-prune` | lease refresh, owner/session updates, linked final receipt, closed metadata | stale in-flight records and invisible abandoned work |
| Task closeout | `repo-contract-kit` | execute and handoff | `make agent-task-cleanup`, `make agent-task-closeout` | nested layout audit, dry-run finished-worktree retention, guarded `git worktree remove` without force | finished sibling worktrees piling up or being removed without durable evidence |
| Session receipt | `repo-contract-kit/workflows/` source, installed by `repo-contract-kit` | verify and handoff | `.agent-workflows/schemas/session-receipt.schema.json` | commands, tests, skipped checks, docs impact, findings, disposition | unverifiable claims of completion |
| Receipt summary | legacy source history; installed successor belongs in `repo-contract-kit` | handoff | `scripts/render_session_receipt_summary.py` | concise human-readable evidence report | humans needing to read full transcripts |
| Trace concept (CLI later) | legacy source concept; future installed behavior belongs in `repo-contract-kit` | handoff and debug | `docs/codex-review-trace.md` | planned local evidence manifest from receipts, summaries, packets, task-status, state-ledger, and finalizer receipts | scattered run evidence or unsafe raw transcript export |
| Docs contract | `repo-contract-kit` | verify | `doc-contract.json`, `scripts/check_doc_impact.py` | docs-impact categories and coverage | behavior or workflow changes without docs updates |
| Docs-impact benchmarks | `agent-workflow-kit` | verify | `research/docs-impact-benchmarks/`, `scripts/run_docs_impact_benchmarks.py` | expected pass/fail cases for categories, waivers, false-positive guards, and false-negative guards | docs-impact precision drifting before broader automation trusts it |
| Docs freshness | `repo-contract-kit` | verify | `make docs-freshness`, `scripts/check_docs_freshness.py` | local link, Make target, script, schema, and semantic-receipt checks | docs changing in the right place but becoming stale or untrue |
| Instruction hygiene | `repo-contract-kit` | verify | `scripts/lint_agent_docs.py`, `.agent-workflows/instruction-budgets.json` | bloat, stale command, unsafe rule, and provenance warnings | root instructions becoming stale or contradictory |
| Token budget | `repo-contract-kit` install layer and workflow source | verify | `make agent-token-budget`, `scripts/check_token_budget.py` | estimated token footprint for agent-facing context files | context growth silently increasing cost, latency, and context loss |
| Regression fixtures | `agent-workflow-kit` | verify | `research/agentic-regression-research/`, `scripts/run_agentic_regression_fixtures.py` | pass/fail fixture results and generated task packets | prompt/workflow changes breaking known agent behaviors |
| Prompt regression fixtures | `agent-workflow-kit` | verify | `research/prompt-regression-fixtures/`, `scripts/run_prompt_regression_fixtures.py` | persona and synthesis golden payload outcomes, including advisory comment/docstring drift labels and false-positive notes | malformed, low-signal, unlabeled drift, or duplicate prompt outputs passing as useful findings |
| Version gate | `repo-contract-kit` | release | `VERSION`, `CHANGELOG.md`, `scripts/version.py` | SemVer validity and release-impact check | shipping workflow changes without release accounting |

## Quality Gates

Each harness change should answer five questions before it is considered done:

1. What agent behavior does this component shape?
2. What evidence proves it ran or was followed?
3. What failure mode does it prevent or expose?
4. Which repo owns the source of truth?
5. Which local command verifies it?

Treat metrics as harness evidence, not vanity counters. A metric is accepted only
when it has an owner, an emission point, and a clear interpretation.
Review outcome and effort metrics are calibration evidence, not productivity
proof. Higher finding volume or shorter generation time is not useful by itself;
interpret yield beside severity, false-positive notes, duplicate rate, human
decisions, review time, and validation quality.

Recurring research adds a novelty gate to the evidence-first flow. Briefs carry
prior-question fingerprints, recent-topic summaries, a novelty threshold, and
rejected or deferred leads. Synthesis scores candidate ideas for novelty,
evidence strength, fit, effort, risk, recommendation state, and rationale before
it proposes backlog edits. Low-novelty repeats stay in rejected/deferred carry
forward state unless new evidence changes the decision.

| Metric family | Required fields | Emission point | First gate |
| --- | --- | --- | --- |
| Receipt completeness | commands, tests, docs impact, skipped checks, disposition | session receipt and receipt summary | `scripts/verify_agent_receipt.py --strict` |
| Scope drift | allowed paths, protected paths, changed paths, undeclared changes | task packet, git diff, and receipt | compare declared scope with `git diff --name-only` |
| Docs-impact coverage | changed-path categories, expected docs, docs updated, no-docs reason | startup packet, docs localizer, and receipt | `python3 scripts/check_doc_impact.py` |
| Docs-impact precision | case id, intent, expected status, expected categories, actual result | docs-impact benchmark runner | `python3 scripts/run_docs_impact_benchmarks.py` |
| Context economy | prompt footprint, context footprint, artifact footprint, retained required evidence | context packet, research artifacts, and token-budget report | `make agent-token-budget` |
| Context relevance | callers, tests, docs, ADRs, scripts, runtime configs, clusters, exclusions, omissions | context packet, context bundle, and review map | context-packet review, context-bundle review, review-map validation, and fixtures |
| Permission fit | trust profile, allowed tools, denied surfaces, mutation attempts | startup packet, review run, and receipt | policy validation before execution |
| Research novelty | prior fingerprints, recent topics, novelty threshold, candidate scores, rejected/deferred carry-forward | research brief and synthesis | `schemas/research-brief.schema.json`; `schemas/research-synthesis.schema.json` |
| Goal alignment | repo goal, affected area contracts, alignment decision, adaptation-needed flag, stop conditions | task packet | `schemas/task-packet.schema.json` |
| Previous task closeout | report sources, active tasks, blockers, dirty/stale state, finalizer receipts, blocker receipts, safe/refuse/escalate decision | task packet | `schemas/task-packet.schema.json`; `make agent-task-status` |
| Fixture coverage | fixture id, failure mode, expected output, pass/fail | regression and benchmark harnesses | `python3 scripts/run_agentic_regression_fixtures.py`; `python3 scripts/run_docs_impact_benchmarks.py`; `python3 scripts/run_prompt_regression_fixtures.py` |
| Review outcome | total, open, accepted, rejected, fixed, deferred, duplicate, false-positive, yield, rate, and human-decision counts | review synthesis, session receipt, and receipt summary | `scripts/verify_agent_receipt.py --strict`; disposition review |
| Effort and human burden | duration_ms, first_finding_latency_ms, time_to_green_ms, commands, token counts, known cost, human_review_minutes, interruptions, notes | session receipt and receipt summary | receipt validation plus human interpretation of unknown or unavailable values |

Metric placement should stay close to the workflow stage that can verify it:

- startup packets and context bundles should emit baseline risk, trust, dirty
  files, docs-impact categories, goal alignment, active-task warnings, token
  footprint, and explicit omissions
- task packets should hold declared scope, protected files, repo and area goal
  alignment, previous task state, closeout-before-start decision, expected
  validation, closeout requirements, docs impact, and approval state
- session receipts should record actual commands, checks, skipped work,
  mutations, docs coverage, final disposition, and optional outcome/effort
  metrics only when grounded in real findings, timings, token/cost data, or
  observed human burden
- receipt summaries should compress the evidence into the human review surface
- review maps should organize large changesets from context packets or context
  bundles into clusters, entrypoints, contracts, risks, sequence, validation
  evidence, and explicit omissions without replacing direct inspection
- trace evidence should compose receipts, summaries, packets, review maps,
  task-status, state-ledger, and finalizer receipts without automatic
  transcript export
- regression fixtures should preserve required fields when prompts, adapters, or
  compaction rules change

Prompt and verification flows should consume compact deterministic reports
before broad repo rereads. When `agent-context-bundle`, `agent-start`,
`agent-next`, `goal-check`, `agent-task-status`, or `agent-token-budget` is
missing, stale, blocked, ambiguous, or omits a required field, agents should
escalate to scoped source inspection and record the omission instead of
treating the report as complete.

Task startup is closeout-first. A new write-capable task should not begin until
the packet records previous task state and a `safe-start` decision backed by
finalizer or equivalent receipt evidence. Missing, stale, blocked, dirty, or
ambiguous prior work should become a refusal or blocker-escalation that names
the next local proof command or receipt instead of mutating unrelated work.

## Source Boundary

Target-repo operators should only see `repo-contract-kit`. Live ownership is:

- `repo-contract-kit/workflows/` owns portable harness concepts: prompts,
  schemas, policies, receipts, task-packet contracts, research workflow design,
  and source-side docs.
- `repo-contract-kit` owns installed execution: Make targets, target-repo
  scripts, managed files, task worktree creation, docs-contract checks,
  instruction linting, install/update behavior, and target-repo templates.
- this checkout preserves historical evidence until archive closeout.

If a harness improvement changes installed behavior, target-repo scripts,
managed templates, prompts, schemas, policies, or conceptual contracts, it now
starts in `repo-contract-kit`.

## Remaining Work

The first backlog, lifecycle, docs-freshness, receipt-metric, and token-budget
checks now have executable surfaces. The remaining work should focus on gates
that compare declared intent with actual integrated output.

| Candidate | Owner | Shape |
| --- | --- | --- |
| Harness regression fixture expansion | `agent-workflow-kit` | add fixtures for scope drift, missing context, incomplete receipts, and permission mismatch |
| Task-worktree readiness gate | `repo-contract-kit` | compare actual changed files, declared scope, receipt validity, docs impact, branch freshness, and active overlaps |
| Semantic docs review receipt | `repo-contract-kit` | make `DOCS_REQUIRE_SEMANTIC=1` practical for higher-risk documentation changes |
| Strict report-routing regression gates | `agent-workflow-kit` and `repo-contract-kit` | compare compact report use, scoped source escalation, preserved evidence fields, and omissions across prompts, receipts, and installed command output |
| Strict token budgets | `agent-workflow-kit` and `repo-contract-kit` | add repo-specific `.agent-workflows/token-budgets.json` files once the warning reports have enough history |

Keep target-facing ownership simple: installed command behavior and target-repo
templates land in `repo-contract-kit`. Source-side prompt/schema concepts start
here only until the `AGW-100` consolidation decision is implemented.
