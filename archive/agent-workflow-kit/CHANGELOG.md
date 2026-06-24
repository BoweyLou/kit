# Changelog

## 0.2.34 - 2026-06-23

- Close `AGW-124` by adding target-owned root `Makefile` wrappers for the
  installed-kit commands advertised in active operator docs, including
  goal/context/ledger/readiness/preflight/self-heal/docs/task/automation and kit
  migration surfaces.
- Document the legacy dogfood wrapper strategy and add a regression test that
  fails when active operator docs mention a `make` command missing from this
  checkout's root `Makefile`.

## 0.2.33 - 2026-06-23

- Close `AGW-123` by updating legacy source route maps so new workflow-source
  edits route to `repo-contract-kit`'s `workflows` directory while this checkout
  keeps `workflows/prompts/` and `.codex/prompts/` as archive mirrors.
- Refresh the self-dogfood checker, ADR 0002, working-rhythm docs, and focused
  tests so local validation enforces the legacy/archive boundary.

## 0.2.32 - 2026-06-22

- Dogfood repo-contract-kit 0.6.5 from local source ref `d4d7910`,
  including managed `docs/upgrade-flow.md` guidance for status, dry-run,
  conflict review, metadata-only migration, managed update, doctor, and
  verification.
- Close `AGW-060` after validating an older dummy target migration preserves
  customized root `AGENTS.md`, keeps dry-run non-mutating, and writes conflict
  proposals instead of overwriting target instructions.

## 0.2.31 - 2026-06-22

- Dogfood repo-contract-kit 0.6.4 from local source ref `4c829a3`,
  including managed `docs/planning-adapters.md` examples for Keryx, Obsidian,
  issue trackers, spreadsheets, and repo backlog mirrors.
- Close `AGW-059` after validating the examples stay docs-only: no external
  service clients, credentials, hosted writes, vault writes, issue mutation, or
  repo-contract-kit priority ownership were added.

## 0.2.30 - 2026-06-22

- Dogfood repo-contract-kit 0.6.3 from local source ref `d4a22f0`,
  including opt-in Node and Python stack profiles with managed local command
  hints and operator docs.
- Close `AGW-058` after validating that the profiles install useful stack
  hygiene defaults without dependency installation, lockfile generation,
  virtual environment creation, package publishing, or framework scaffolding.

## 0.2.29 - 2026-06-22

- Add optional `phase_files` task-packet metadata plus prompt/template guidance
  for splitting large reviews or implementations into bounded fresh-session
  phases without replacing task packets or widening scope.
- Teach planner, implementer, and verification prompts to preserve current
  phase scope, completion evidence, and handoff notes, with generated Codex
  adapters refreshed.

## 0.2.28 - 2026-06-22

- Dogfood repo-contract-kit 0.6.2 from local source ref `be27b2f`,
  including docs-only merge-governance examples for GitHub protected branches,
  required status checks, and merge queue handoff.
- Close `AGW-053` after validating that hosted PR and queue authority remains
  outside repo-contract-kit: no GitHub API calls, credentials, PR comments,
  labels, approvals, queue mutation, merge action, or branch-protection mutation
  were added.

## 0.2.27 - 2026-06-22

- Dogfood repo-contract-kit 0.6.1 from local source ref `76e2129`,
  including the top-level `kit update --json` apply-by-default migration fix
  and installed operator guidance.
- Preserve customized source-repo managed files as update conflicts under
  `.doc-contract-kit/updates/` while updating the managed CLI script,
  workflow docs, and install metadata.

## 0.2.26 - 2026-06-22

- Dogfood repo-contract-kit 0.6.0 from local source ref `10e7542`,
  including the docs-as-tests manifest v2 checker and installed operator
  guidance.
- Close `AGW-101` after validating explicit local OpenAPI and JSON claim
  checks, skipped/unsupported/refused result states, no target writes/network
  use, and source backlog/summary alignment.

## 0.2.25 - 2026-06-22

- Dogfood repo-contract-kit 0.5.0 from local source ref `79bb855`,
  including the refreshed kit-managed scripts, docs, area-contract scaffolding,
  and update metadata in this source checkout.
- Close `AGW-100` after validating the public `kit` product surface, structured
  update evidence, root `AGENTS.md` preservation, and clean/customized older
  target migration path.

## 0.2.24 - 2026-06-16

- Add review-only local-model suitability guidance to the local/private review
  policy, including data-boundary labels, capability caveats, and escalation
  triggers for high-risk or low-confidence reviews.
- Update runtime compatibility and operator docs with source-cited local/Ollama
  notes for Codex, Continue, Goose, Aider, and community Open Codex forks
  without adding generated adapter support claims.

## 0.2.23 - 2026-06-16

- Add optional session receipt metrics for review outcome and effort, including
  review yield, false-positive and duplicate rates, latency, time-to-green,
  token/cost effort, and human review burden.
- Validate and summarize the optional metric groups without making them required,
  and update synthesis/docs guidance so unknown metrics are omitted or caveated
  rather than guessed.

## 0.2.22 - 2026-06-16

- Teach the learning-comments prompt to consume existing agent-start,
  session-start, context-packet, context-bundle, and task decision evidence
  before manual ADR scanning.
- Define the no-ADR fallback for learning-comments work so agents record missing
  decision records, use README/docs/tests/code/config/changelog/task evidence
  instead, keep unsupported architecture claims out of comments, and refresh
  docs, tests, and generated Codex adapters for the prompt workflow.

## 0.2.21 - 2026-06-16

- Add a runtime compatibility matrix for Codex, Claude Code, Cursor, Continue,
  GitHub Copilot, Goose, Aider, Cline, and Roo Code, including current
  generated/planned/manual-only status, install-layer boundaries, validation
  source URLs, access dates, limitations, and privacy/locality guidance.
- Link the matrix from the README, runtime adapter guide, and workflow stack
  map so operators can distinguish source-generated adapters from
  repo-contract-kit target-install adapters before adding runtime support.

## 0.2.20 - 2026-06-16

- Add a large-changeset review-map artifact contract with
  `workflows/prompts/templates/review-map.md` and
  `schemas/review-map.schema.json`, covering source inputs, changed-file
  clusters, inspection targets, risk hotspots, reviewer routing, review
  sequence, validation evidence, omissions, and follow-up task-packet
  candidates.
- Include the review-map template in the review skill-pack surface and refresh
  generated Codex prompt adapters and docs so review maps compose with
  `make context-packet` or installed context bundles without replacing direct
  source, tests, docs, ADR, script, runtime-config, or receipt inspection.

## 0.2.19 - 2026-06-15

- Add advisory comment/docstring drift guidance to the documentation/code delta
  reviewer, including two-sided evidence requirements, drift labels, and
  false-positive handling for generated/vendor, historical, convention,
  simplified-example, and speculative cases.
- Extend review finding and synthesis guidance plus prompt regression fixtures
  so comment/docstring drift labels stay advisory, evidence-backed, and
  non-blocking unless concrete public/runtime/security/ops impact raises
  severity.

## 0.2.18 - 2026-06-15

- Add a closeout-first task-packet startup contract with required
  `previous_task_state` and `closeout_required_before_start` fields so handoffs
  can distinguish safe starts, refused starts, and blocker escalations before
  implementation edits.
- Update implementation, maintainer, verification, docs, and regression
  fixture checks so unresolved prior task state needs finalizer, task-status,
  closeout, self-heal, blocker receipt, or owner escalation evidence before work
  is marked ready.

## 0.2.17 - 2026-06-15

- Teach task-packet, maintainer-queue, verification, and prompt-index guidance
  to prefer compact deterministic reports before broad repo rereads while
  preserving scoped source fallback and omission evidence.
- Add a deterministic-report-routing regression control so fixture validation
  catches prompt or docs drift that would hide required scope, docs impact,
  goal alignment, validation, closeout, or receipt evidence.

## 0.2.16 - 2026-06-15

- Add a task-packet goal-alignment contract with repo goals, affected area
  contracts, alignment decisions, adaptation-needed flags, and stop conditions
  before implementation handoff.
- Refresh task-packet prompts, schema, docs, generated adapters, and regression
  fixture defaults with the source-side contract that AGW-091 can later feed
  with deterministic installed reports.

## 0.2.15 - 2026-06-15

- Add research novelty-ledger fields to briefs and candidate scoring to
  syntheses so recurring backlog research can reject low-novelty repeats and
  carry rejected or deferred leads forward.
- Refresh research prompts, generated Codex adapters, docs, and local research
  templates with the novelty/candidate-score contract.

## 0.2.14 - 2026-06-15

- Add prompt regression fixtures and
  `scripts/run_prompt_regression_fixtures.py` for deterministic persona and
  synthesis payload checks around schema handling, evidence quality, nit
  suppression, source-persona preservation, and duplicate finding discipline.
- Wire the prompt regression runner into local validation and document the new
  fixture command.

## 0.2.13 - 2026-06-15

- Add docs-impact benchmark fixtures and `scripts/run_docs_impact_benchmarks.py`
  for deterministic false-positive, false-negative, coverage, and waiver
  checks around the installed docs-impact evaluator.
- Document the new benchmark surface and cover it with focused unit tests.

## 0.2.12 - 2026-06-15

- Require strict learning-comments receipts to prove comment-only or
  explanation-note-only scope with `evidence.comment_only_verification`,
  including diff scope, reviewed paths, behavior-change assertions, evidence
  commands, non-comment path explanations, and uncertainty handling.
- Refresh the learning-comments prompt and usage docs so operators know where
  to record behavior-neutral receipt evidence.

## 0.2.11 - 2026-06-15

- Add a manifest-driven Codex skill-pack exporter with `make skill-pack-export`,
  `make skill-pack-check`, and `make skill-pack-list`.
- Document the ignored `dist/codex-skill-pack/` artifact shape, subset export,
  and manual Codex skill installation path.

## 0.2.10 - 2026-06-15

- Require closeout evidence in task-packet prompts, templates, and schema:
  final receipt path, readiness check, lifecycle action, final task-status
  result, closeout preview, and dirty-state explanation before handoff.
- Refresh generated Codex prompt adapters and regression-fixture task packet
  generation so machine-readable packets carry the new closeout requirements.

## 0.2.9 - 2026-06-13

- Generate a GitHub Copilot instructions adapter from the neutral workflow
  source and mark Copilot as a current runtime projection instead of a planned
  adapter.
- Reuse the standalone review-risk classifier from `agent_start.py` so startup
  packets and `scripts/classify_review_risk.py` share one routing source.
- Dogfood `repo-contract-kit` 0.4.29 so this source repo exposes
  `make agent-task-ready` and the automation-safe
  `make agent-automation-handoff` sidecar receipt/patch workflow.

## 0.2.8 - 2026-06-11

- Dogfood `repo-contract-kit` 0.4.27 so this source repo exposes
  `make kit-update-stack` and `make kit-refresh-stack` for target-plus-source
  update runs from one installed target-repo command, with local checkout
  discovery so agents can usually run `make kit-update-stack` without paths.
- Refresh installed workflow docs and the source working rhythm with the
  target repo plus `Codex_CodeReview` update path.

## 0.2.7 - 2026-06-11

- Dogfood `repo-contract-kit` 0.4.26 so this source repo exposes
  `make agent-task-closeout` for preview-first removal of eligible finished
  sibling task worktrees.
- Mark `AGW-080` complete and refresh the backlog split, feature matrix,
  working rhythm, harness map, and installed workflow docs with the
  evidence-gated closeout and retention behavior.

## 0.2.6 - 2026-06-10

- Dogfood `repo-contract-kit` 0.4.25 so `make agent-start` reports the
  selected backlog source contract instead of only checking `docs/backlog.md`.
- Refresh `REVIEW.md` and `.agent-workflows/README.md` so the local docs
  contract, docs-freshness gate, backlog commands, task lifecycle commands, and
  token-budget command are aligned with the installed command surface.

## 0.2.5 - 2026-06-09

- Expand `codebase-learning-comments.md` for non-developer explainability:
  sparse inline comments remain behavior-neutral, while broader plain-language
  context moves into a separate explanation note.
- Add active-task coordination and harness metric fields to task-packet and
  session-receipt schemas, then refresh the canonical task-packet prompt,
  template, and generated Codex adapter.
- Dogfood `repo-contract-kit` 0.4.24 with backlog status/check and
  `agent-next`, task lifecycle/lease commands, docs-freshness checks,
  behavior-changing receipt evidence enforcement, and token-budget reporting.
- Mark the completed AGW backlog slices and refresh split backlog views,
  feature matrix, harness docs, working rhythm, and source repo command docs.

## 0.2.4 - 2026-05-28

- Dogfood `repo-contract-kit` 0.4.19, including the managed kit Makefile
  fragment, task-worktree cleanup script, primary-checkout guard, kit status
  boundary explanation, and Makefile include-aware agent docs linting.
- Expose `make kit-explain` from the source repo and keep `make kit-update` /
  `make kit-refresh` wired to the explicit `--apply` update path.

## 0.2.3 - 2026-05-25

- Add `task-worktree-cleanup.md` to guide safe inventory, flattening, and
  removal decisions for messy task-worktree layouts.
- Refresh the generated Codex prompt adapter and prompt index with the cleanup
  workflow.

## 0.2.2 - 2026-05-19

- Add `docs/agent-workflow-stack.md` as the source-side map for
  `agent-workflow-kit`, `repo-contract-kit`, and installed target repositories.
- Add `make stack-status KIT=/path/to/repo-contract-kit` to show source-repo
  status, self-dogfood boundary checks, companion kit checkout state, and
  installed kit/prompt snapshot provenance in one command.
- Mark the paired `AGW-064` / `AGW-065` operator-clarity backlog slice complete
  and refresh the backlog summary.

## 0.2.1 - 2026-05-19

- Dogfood `repo-contract-kit` 0.4.8 so this source repo exposes
  `make kit-refresh KIT=/path/to/repo-contract-kit` for clean local kit pulls
  followed by the safe managed update path.
- Restore source-repo Make targets for targeted research and
  worktree-per-task preparation so installed helper scripts and documented
  commands stay aligned.
- Refresh local guardrail docs, install receipts, and managed manifests to the
  current kit and prompt snapshot while preserving the source-repo prompt
  ownership boundary.

## 0.2.0-beta.11 - 2026-05-19

- Add a targeted research workflow module with research briefs,
  source-specific GitHub, arXiv, Hacker News, and official-docs prompts,
  research synthesis, and research-to-work handoff guidance.
- Add schemas for research briefs, source reports, and research synthesis
  outputs so source agents can feed backlog, review, design, architecture, ADR,
  risk, or task-packet proposals without directly mutating repo files.
- Require bounded source plans with seed URLs or exact queries, allowed domains,
  include/exclude terms, artifact types, result budgets, and quality floors so
  research agents do not drift into random web searches.
- Refresh the generated Codex prompt adapter with the new research prompts.

## 0.2.0-beta.10 - 2026-05-19

- Add `docs/working-rhythm.md` as the human-facing mental model for the
  orient, review, scope, and execute flow across `agent-workflow-kit`,
  `repo-contract-kit`, and installed target repositories.
- Add `make workflow-help` / `make help` so the source repo has a concise
  command entrypoint before deeper docs.
- Route README, prompt-kit usage docs, and local workflow mechanics back to the
  working rhythm.

## 0.2.0-beta.9 - 2026-05-14

- Document the worktree-per-task runner pattern for write-capable agent tasks
  and mark the paired `AGW-039` / `AGW-061` isolation slice complete in the
  ecosystem backlog.
- Add a self-dogfood boundary ADR and `make self-check` so this repo can use
  repo-contract-kit guardrails without confusing installed files with the
  canonical workflow source.
- Verify that `workflows/prompts/` stays canonical, `.codex/prompts/` stays a
  generated mirror, expected kit localizations are explicit, and `kit-update`
  remains manual.

## 0.2.0-beta.8 - 2026-05-14

- Dogfood `repo-contract-kit --preset agentic` in this source repo with local
  docs-contract files, agent workflow receipts, instruction hygiene checks,
  Make targets, and repository-specific documentation impact rules.
- Preserve `workflows/prompts/` as the canonical prompt source while using
  `.codex/prompts/` as the generated Codex adapter for local agent workflows.

## 0.2.0-beta.7 - 2026-05-14

- Mark AGW-038 complete after adding repo-contract-kit instruction hygiene
  guidance and instruction-budget checks that keep accepted findings from
  bloating root agent instruction files.
- Add AGW-061 for a repo-contract-kit `agent-task-prepare` command that
  prepares isolated per-task worktrees for concurrent write-capable agents.
- Refresh backlog split views and summary counts.

## 0.2.0-beta.6 - 2026-05-14

- Add deterministic review-risk classification for changed paths, including
  risk tier, trust profile, triggers, specialist persona routing, and tests.
- Add read-only reviewer, local/private review, browser research, and
  review-risk policy prompts, then refresh the generated Codex prompt adapter.
- Extend session receipts and persona manifests with review-risk and policy
  metadata.

## 0.2.0-beta.5 - 2026-05-14

- Add explicit backlog rows for repo-contract-kit stack-aware profiles,
  planning/memory adapter examples, and richer guided upgrade flows.
- Regenerate the repo-owned backlog views and refresh the backlog status count.

## 0.2.0-beta.4 - 2026-05-14

- Add script-flow and function-guide comments across the workflow-kit scripts
  so maintainers can trace each command's execution path and helper roles.

## 0.2.0-beta.3 - 2026-05-13

- Split the aggregate AGW backlog into generated `agent-workflow-kit` and
  `repo-contract-kit` views while keeping the cross-repo backlog as the source.
- Add `scripts/split_backlog_by_repo.py`, `make backlog-split`, and
  `make backlog-split-check`; `make validate` now checks the split files.
- Document the repo-boundary rule: check both local repos before implementing
  cross-repo backlog work and update both when required.
- Sanitize research provenance wording to remove named and browser-specific
  collection details while preserving read-only/authenticated caveats.

## 0.2.0-beta.2 - 2026-05-13

- Add a neutral workflow prompt source under `workflows/prompts/` and record
  generated and planned runtime adapters in `workflows/manifest.json`.
- Add `scripts/export_workflow_adapters.py`, `make prompt-adapters-export`, and
  `make prompt-adapters-check` so `.codex/prompts/` is generated and validated
  from the canonical source.
- Document runtime adapter boundaries and mark AGW-041 complete.

## 0.2.0-beta.1 - 2026-05-13

- Add session receipt Markdown summaries for completed local agent runs.
- Add deterministic diff-to-context packets with likely callers, tests, docs,
  ADRs, scripts, and runtime configs.
- Mark the remaining partial backlog items complete and refresh the research
  summary status.

## 0.1.0 - 2026-05-13

- Establish the first local SemVer baseline for agent-workflow-kit.
- Add commit-time versioning checks for workflow, prompt, schema, script, and governance changes.
