# Agentic Development Workflow Research Synthesis

Generated: 2026-04-29

This folder consolidates six focused research streams into a source-level JSON
report, a feature comparison CSV, and a backlog CSV.

Naming note: this work was historically split across **agent-workflow-kit**,
the portable workflow/prompt/schema layer, and **repo-contract-kit**, the
installable repository contract and local guardrail layer. `AGW-100` simplified
that model: target-repo operators should see only the global `repo-contract-kit`
installer and CLI, and canonical workflow source now lives under
`repo-contract-kit/workflows/`.

## Local-Only Constraint

The baseline is now local-first and agent-tool agnostic:

- no GitHub Actions, hosted CI, or GitHub-specific PR surface is required
- AmpCode, Codex, and other coding agents consume the same Markdown prompts,
  JSON schemas, local scripts, and `make` targets
- GitHub Actions, slash commands, and PR comments can be added later as optional
  adapters over the same local contract

## Files

- `source_findings.json`: source summaries, current-repo baseline, feature matrix, and backlog.
- `feature_matrix.csv`: feature areas compared against what agent-workflow-kit and repo-contract-kit already provide.
- `backlog.csv`: aggregate cross-repo implementation backlog with priority, owning repo, source examples, and delivery shape.
- `agent-workflow-kit-backlog.csv`: generated repo-owned view for prompt, schema, receipt, task-packet, eval, and adapter-source work in this repo.
- `repo-contract-kit-backlog.csv`: generated repo-owned view for installer, target-repo policy, local checks, update, CI/PR adapter, runtime interop, and consolidated workflow-source work.
- `spikes/`: bounded research notes for follow-on work that should not ship
  runtime behavior in the same change.

## Task Packet Handoff Rule

When a change adds or updates a task packet under
`research/agentic-workflow-review/task-packets/`, treat it as research backlog
state. The same change must either update this summary with the affected
backlog id, current state, and handoff or closeout note, or carry an explicit
`No docs needed: <reason>` declaration when the packet is archival and no
research state changed.

Run `python3 scripts/check_doc_impact.py --working-tree` before the broader
`make docs-check` gate. The working-tree check catches packet-only gaps that a
branch-level docs check can miss when earlier commits already changed the
summary. If a packet closes or changes a backlog row, also run
`make backlog-check && make backlog-split-check` so the aggregate and generated
repo-owned backlog views stay aligned.

## Main Readout

1. Make repo-contract-kit the only normal product surface: one global cURL
   installer, one CLI, and explicit per-repo `target add`, `target status`, and
   `target update` commands.
2. Treat this agent-workflow-kit checkout as legacy source history; new
   workflow-source edits start under `repo-contract-kit/workflows/`.
3. Keep target repos free of nested source checkouts: they receive installed
   guardrails, prompt snapshots, provenance, and safe update metadata from
   `repo-contract-kit`.
4. Treat agent instructions as code: lint paths, commands, bloat, contradictions, hidden Unicode, permissions, and stale references.
5. Require evidence receipts before trusting agent work: commands run, tests passed, checks skipped, diff summary, docs impact, findings, and disposition.
6. Use multi-agent review selectively: a small localizer/reviewer for normal PRs, specialist fleets only for high-risk changes.
7. Measure review yield and false positives before adding more autonomy.
8. Use repo-contract-kit's `make agent-start` as the first local runner bridge:
   it creates a local session packet with changed files, docs impact, latest ADR
   context, kit/update status, target repo version, prompts, personas, and a
   receipt template without requiring hosted CI or a specific agent runtime.
9. Prefer repo-contract-kit's global `self status`, `self update`,
   `target status`, and `target update` commands over target-local
   `KIT=/path` maintenance flows.
10. Use `make stack-status KIT=/path/to/repo-contract-kit` only for archive or
   migration validation of this legacy source checkout.
11. Use repo-contract-kit's `make agent-task-status` before launching or
   handing off parallel write-capable tasks so active scopes, sibling
   worktrees, stale metadata, task leases, linked receipts, and coordination
   hazards are visible locally.
12. Treat the workflow stack as an emerging agent harness: startup packets,
   context packets, permission policies, task worktrees, receipts, targeted
   research, regression fixtures, and docs gates should be mapped and improved
   as a coherent harness rather than as disconnected helper commands.
13. Make token efficiency an explicit workflow-design constraint across
   prompts, context packets, adapters, receipts, research artifacts, and
   execution loops, with compaction rules that preserve required evidence and
   safety boundaries.
14. Treat backlog management as a portable source contract and handoff path,
   not as a standalone backlog app: repos may prioritize work in Keryx, issues,
   CSV, or Markdown mirrors, but selected items should validate and convert
   cleanly into task packets.
15. Add executable freshness checks beside path-based docs impact so local
   Markdown links, documented Make targets, script references, schema
   references, and high-risk semantic review receipts stay verifiable.
16. Treat completed task-worktree cleanup as an evidence-gated closeout and
   retention problem: preserve receipts and reviewable branch state, preview by
   default, and remove only clean terminal worktrees through explicit apply or
   configured retention.
17. Treat maintainer-orchestration skills as pattern libraries unless their
   authority model matches this stack: queue briefs can borrow classification,
   monitoring, proof, and owner-decision shapes, but PR mutation, releases,
   credential use, and thread management stay behind explicit local contracts.
18. Treat dirty-state startup failures as a first-class harness problem: agents
   need kit-native preflight receipts, actionable dirty blockers, task
   finalizers, automation baseline receipts, and prompt-level closeout evidence
   so live work, sidecar state, and parallel worktrees remain explainable.
19. Keep dirty-state recovery evidence-gated: baseline-tolerant task starts,
   guarded self-heal, local receipt ledgers, closeout-first prompts, and
   thread/session attribution are now installed so agents can recover without
   deleting user work or hiding parallel activity.
20. Treat task completion and docs/code alignment as a single finish-gate
    design problem: agents need one approved exit ramp that composes docs
    alignment, strict receipts, readiness, optional local commits, finalization,
    task status, and closeout/prune evidence rather than relying on memory to
    run separate commands in the right order.
21. Treat lite mode as a product contract, not a bypass: small repos and
    low-risk local tasks should get a short setup/orient/plan/verify path, but
    public behavior, schema, release, privacy, dirty-state, or parallel-agent
    triggers must escalate to standard or release-gated harness modes.

## Current Spike Notes

- `spikes/agw-034-lsp-context-lookup.md`: recommends optional local-only LSP
  context artifacts later, with deterministic context packets and review maps
  kept as the required fallback.
- `spikes/agent-run-completion-and-guardrails.md`: recommends `AGW-103`
  through `AGW-106` candidate slices for a task-complete finish gate, docs
  alignment aggregate, run profile/chunk plan, and worktree retention sweep.
- `spikes/kit-cli-interactivity-and-smarts.md`: recommends adding a structured
  `kit` command map/agent-context surface, better parse errors, grouped
  human help/status, shell completions, and a TTY-only command palette before
  considering any larger TUI rewrite.
- `spikes/lite-mode.md`: defines a proposed lite/standard/release-gated mode
  model so `repo-contract-kit` can keep safety defaults while reducing ceremony
  for small repos and low-risk local tasks.

## Current Lite Mode Backlog Cluster

Implemented in `repo-contract-kit` 0.6.25. The shipped surface is
`kit setup --preset lite`, `kit mode-check --json`,
`kit task-packet --harness-mode auto --json`,
`kit verify --harness-mode auto --json`, `kit calibration --json`, and
`kit retention --json`, with generated CLI reference, docs freshness, version
check, and full source tests passing.

| ID | Priority | Status | Note |
| --- | --- | --- | --- |
| `AGW-132` | P0 | done | Lite/standard/release-gated contract and mode matrix shipped in docs and templates. |
| `AGW-133` | P0 | done | Lite preset and no-prompt-pack install path shipped with regression coverage. |
| `AGW-134` | P0 | done | Task packets now accept `--harness-mode`; lite emits compact notes and escalation triggers. |
| `AGW-135` | P1 | done | Primary path is status, mode-check, task-packet, verify, update dry-run. |
| `AGW-136` | P1 | done | `kit calibration --json` reports local harness outcome fields read-only. |
| `AGW-137` | P1 | done | Sidecar retention/privacy policy and purge preview shipped; no deletion by default. |
| `AGW-138` | P2 | done | Version 1 archive checklist and old checkout notice now redirect normal source work. |
| `AGW-139` | P0 | done | `kit mode-check --json` selects strictest applicable mode with trigger evidence. |

## Repo Boundary Rule

Before implementing any AGW backlog item, check whether the work is
operator-facing, workflow-source-facing, or archive/history-facing.
Operator-facing and workflow-source-facing work now belongs in
`repo-contract-kit` and should preserve the one-CLI target-repo experience.

- `repo-contract-kit/workflows/` owns live prompts, personas, schemas, receipt
  formats, task packets, canonical workflow prompt sources, and generated
  target template source.
- `repo-contract-kit` owns installer behavior, target-repo managed files,
  `AGENTS.md`/`REVIEW.md`, `.agent-workflows/`, `.codex/prompts/` generation,
  local Make targets, update/migration commands, versioning profile, docs
  contract checks, and CI/PR/runtime adapters.
- this checkout owns historical evidence until archive closeout; do not start
  new normal source work here.

If historical source material is needed, cite it as migration evidence in the
`repo-contract-kit` change rather than re-opening a two-repo workflow.

## Maintainer Orchestration Pattern Review

The external `maintainer-orchestrator` skill is useful as a pattern source, not
as a file to vendor directly. Its strongest reusable ideas are queue
classification, decision-ready owner asks, worker monitoring, authorization
boundaries, live-proof gates, and release-readiness checks.

The mismatch is authority and scope. That skill is GitHub, PR, release,
credential, and thread-control heavy; this stack stays local-first and
read-only-by-default until a task packet, permission profile, or explicit owner
request grants more authority.

Local mapping:

- queue discovery: `make agent-next` and `make backlog-status`
- delegation: task packets plus `make agent-task-prepare`
- monitoring: `make agent-task-status` and lifecycle heartbeat/finish/block
- decision-ready proof: receipts plus `python3 scripts/agent_task_ready.py`
- automation handoff: `make agent-automation-handoff`

Follow-on `AGW-084` captures the source-side prompt work: a maintainer queue and
owner-decision brief that renders `Active`, `Needs owner`, `Ready next`, and
`Blocked` sections from existing backlog, task-status, receipt, and readiness
signals without adding a new public CLI or installed target-repo API.

## Highest Priority Backlog Slice

| ID | Status | Note |
| --- | --- | --- |
| `AGW-001` | done | repo-contract-kit's `--preset agentic` now installs the local-agentic, review-prompts, and test-first profiles. |
| `AGW-002` | done | `lint_agent_docs.py` covers hidden Unicode, strict paths, stale command/script references, contradiction warnings, rule bloat/provenance warnings, unsafe guidance, and JSON/SARIF output. |
| `AGW-007` | done | Session receipt schema exists in agent-workflow-kit and is mirrored into repo-contract-kit templates. |
| `AGW-008` | done | `scripts/render_session_receipt_summary.py` renders concise Markdown from completed receipts; `make receipt-summary RECEIPT=...` exposes the handoff path. |
| `AGW-009` | done | Persona manifest schema and local-first/tool-agnostic manifest exist. |
| `AGW-011` | done | repo-contract-kit installs `REVIEW.md` by default and supports `--include-design` to install optional `DESIGN.md` design-intent contracts. |
| `AGW-012` | done | repo-contract-kit 0.4.35 adds explicit runtime adapter selection, managed `CLAUDE.md` and `.github/copilot-instructions.md` adapters, runtime-adapter receipt/manifest/status metadata, and update-safe conflict handling. |
| `AGW-013` | done | Review-risk classifier emits risk tier, trust profile, trigger rules, guidance, and specialist persona routing. |
| `AGW-014` | done | repo-contract-kit installs `scripts/agent_review_run.py` and `make agent-run-review`; manual mode writes JSON placeholders and Amp mode executes read-only persona prompts with mutation checks. |
| `AGW-015` | done | TDD prompts and receipts now capture red/green evidence, generated-test provenance, and skip reasons. |
| `AGW-016` | done | repo-contract-kit 0.4.24 validates behavior-changing receipt scope and requires red/green evidence or an explicit skip reason in strict checks. |
| `AGW-018` | done | Local docs-impact JSON localizer maps changed paths to doc categories and suggested docs. |
| `AGW-019` | done | repo-contract-kit 0.4.36 adds `docs-propose` / `make agent-docs-propose` to write sidecar docs proposal JSON, Markdown, and `docs.patch` scaffold artifacts without modifying target files. |
| `AGW-020` | done | repo-contract-kit 0.4.37 adds non-mutating `onboarding-pr` branch, install, validation, commit, push, and manual PR instructions with optional sidecar JSON/Markdown review bundles. |
| `AGW-021` | done | repo-contract-kit 0.4.49 records `profile_config_schema_version` in install receipts and manifests, reports profile/config schema state in `update-plan`, and adds explicit metadata-only migration through `update.py --apply --metadata-only`, `repo_contract_kit.py migrate-config`, and `make kit-migrate-config` without rewriting target-owned or customized managed files. |
| `AGW-022` | done | repo-contract-kit 0.4.38 installs a docs-contract PR comment workflow and deterministic renderer for status, policy links, category details, and next actions. |
| `AGW-023` | done | repo-contract-kit 0.4.39 installs a spec-only PR slash-command grammar for `/docs-impact`, `/waive-docs`, `/review-docs`, `/add-docs`, and `/update-changelog`. |
| `AGW-024` | done | repo-contract-kit 0.4.50 adds `changelog-update` / `make agent-changelog-update` to propose or strictly check release-note work from docs-impact and versioning context without writing target-owned `VERSION` or `CHANGELOG.md`. |
| `AGW-025` | done | repo-contract-kit 0.4.51 adds `docs-explain` / `make agent-docs-explain` as a deterministic local README/docs/policy explainer with cited snippets, no-match uncertainty, and no target, sidecar, hosted-model, or network writes/calls. |
| `AGW-026` | done | Safe-output schema is installed under `.agent-workflows/schemas/`. |
| `AGW-028` | done | repo-contract-kit installs tool/network allowlist guidance and adds review-risk/trust-profile context to startup receipts. |
| `AGW-029` | done | agent-workflow-kit documents `docs/codex-review-trace.md` as the CLI-later `codex-review trace` concept for local evidence maps over receipts, summaries, packets, task-status, state-ledger, and closeout/finalizer receipts without shipping a command or installed kit behavior. |
| `AGW-030` | done | repo-contract-kit 0.4.52 adds an explicit experimental `docs-as-tests` profile plus `check_docs_as_tests.py`, `repo_contract_kit.py docs-as-tests`, and installed `make docs-as-tests` for manifest-declared local JSON OpenAPI method/path assertions without joining default presets or `docs-check`. |
| `AGW-031` | done | agent-workflow-kit 0.2.19 adds advisory comment/docstring drift labels, two-sided evidence rules, false-positive handling, optional review labels, generated adapters, docs, and PRF-006 prompt regression coverage without adding a scanner, CI gate, or repo-contract-kit behavior. |
| `AGW-032` | done | `scripts/build_context_packet.py` emits changed files, likely callers, likely tests, related docs, ADRs, scripts, runtime configs, and grounding guidance; `make context-packet` exposes it. |
| `AGW-033` | done | agent-workflow-kit 0.2.20 adds a Markdown/JSON review-map artifact contract for large changesets, includes the template in the review skill-pack surface, and documents that review maps compose with context packets or context bundles without replacing direct source inspection. |
| `AGW-034` | done | `research/agentic-workflow-review/spikes/agw-034-lsp-context-lookup.md` recommends a later optional local-only LSP context artifact for definitions/usages while keeping deterministic context packets and review maps as the required fallback; it defines artifact shape, sidecar/cache policy, token/time caps, generated/vendor exclusions, unsupported-language omissions, privacy boundaries, fixture tests, and follow-on backlog shape without shipping runner, CLI, prompt, schema, Makefile, version, or repo-contract-kit behavior. |
| `AGW-035` | done | repo-contract-kit 0.4.53 adds an explicit opt-in `private-context` profile with managed `.agent-context/` README/example templates, privacy warnings, managed `.gitignore` defaults that ignore real local context files, docs, install/update/CLI tests, and no default/minimal/learning/test-first/agentic preset inclusion. |
| `AGW-036` | done | Review prompts now cap findings, suppress nits, require false-positive notes, and track dispositions. |
| `AGW-038` | done | repo-contract-kit installs instruction hygiene guidance and budget checks so accepted findings can become scoped policy without bloating `AGENTS.md`. |
| `AGW-039` | done | Worktree-per-task guidance now defines the write-capable agent flow, explicit scope rules, local task packet and receipt expectations, overlap checks, and human approval gates. |
| `AGW-040` | done | Read-only reviewer sandbox policy and persona-manifest policy metadata make mutation denial explicit. |
| `AGW-041` | done | `workflows/manifest.json` and `workflows/prompts/` now provide the canonical prompt source; `.codex/prompts/` is generated and checked by `make validate`. |
| `AGW-042` | done | agent-workflow-kit 0.2.11 adds manifest-driven Codex skill-pack export targets, deterministic pack manifests, ignored `dist` artifacts, docs, and tests. |
| `AGW-043` | done | agent-workflow-kit 0.2.21 adds `docs/runtime-compatibility.md` with a current runtime matrix for Codex, Claude Code, Cursor, Continue, GitHub Copilot, Goose, Aider, Cline, and Roo Code; the guide records generated/planned/manual-only status, source/install/target ownership, source URLs and access dates, repo-contract-kit adapter boundaries, and privacy/locality guidance. |
| `AGW-044` | done | agent-workflow-kit 0.2.12 adds a learning-comments Comment-Only Receipt section, `evidence.comment_only_verification`, focused receipt tests, docs, and generated adapters; repo-contract-kit 0.4.40 owns the installed strict validator and managed receipt schemas. |
| `AGW-045` | done | agent-workflow-kit 0.2.22 teaches `codebase-learning-comments.md` to consume agent-start, session-start, context-packet, context-bundle, and task decision evidence before manual ADR scanning, and to use explicit no-ADR fallback evidence with uncertainty instead of invented design intent. |
| `AGW-046` | done | agent-workflow-kit 0.2.13 adds deterministic docs-impact benchmark fixtures, a text/JSON runner, docs, and focused tests for true-positive, covered-change, false-positive guard, false-negative guard, and waiver cases. |
| `AGW-047` | done | agent-workflow-kit 0.2.14 adds deterministic prompt regression fixtures plus `scripts/run_prompt_regression_fixtures.py`, covering valid persona findings, malformed persona payloads, low-signal nits, merged synthesis findings with source personas, and duplicate synthesis findings with focused tests and local validation wiring. |
| `AGW-048` | done | agent-workflow-kit 0.2.23 adds optional session receipt outcome and effort metrics for review yield, false-positive and duplicate rates, latency, time-to-green, token/cost effort, and human burden, with validation, receipt summaries, generated adapter refresh, and calibration-not-productivity caveats. |
| `AGW-049` | done | Local/private review policy records data-sent boundaries, provider notes, and stop conditions. |
| `AGW-050` | done | Browser research policy forbids account mutation and defines source-quality/receipt requirements. |
| `AGW-051` | done | agent-workflow-kit 0.2.24 adds review-only local-model suitability guidance, data-boundary labels, escalation triggers, runtime compatibility notes, and source-cited caveats without adding generated runtime adapters or model configuration. |
| `AGW-054` | done | Task-packet prompt, Markdown template, and JSON schema now turn backlog rows, issues, accepted findings, or broad requests into scoped agent work. |
| `AGW-056` | done | Seed agentic-regression fixtures, schema validator, generated task packets, and deterministic golden harness are in place. |
| `AGW-057` | done | repo-contract-kit installs agent permission policy schemas, local-first profiles, review-runner trust validation, docs, and tests. |
| `AGW-061` | done | repo-contract-kit now installs `make agent-task-prepare TASK=<id>` to create a task branch and sibling worktree, local task packet and receipt artifacts, in-flight metadata, and overlap warning/blocking. |
| `AGW-062` | done | agent-workflow-kit now includes a targeted research prompt module, source-specific GitHub/arXiv/Hacker News/official-docs prompts, research schemas, and ADR 0003. |
| `AGW-063` | done | repo-contract-kit now installs a local research runner surface for manual-mode research planning, source prompts, synthesis, and task-packet handoff artifacts. |
| `AGW-064` | done | agent-workflow-kit now has a stack map, ownership decision table, release-pairing guidance, and `make stack-status KIT=/path/to/repo-contract-kit`. |
| `AGW-065` | done | repo-contract-kit now mirrors the stack map from the install-layer side and refreshes installed target-repo working-rhythm guidance. |
| `AGW-066` | done | repo-contract-kit now installs `make agent-task-status` to compare active task metadata against `git worktree list`, report coordination hazards, and support JSON/strict status checks. |
| `AGW-067` | done | repo-contract-kit 0.4.24 adds task lifecycle commands for heartbeat, finish, block, abandon, receipt linking, and prune. |
| `AGW-068` | done | repo-contract-kit 0.4.24 adds prepare locking, run ids, owner/session metadata, heartbeat timestamps, and lease expiry. |
| `AGW-069` | done | Task packets and receipts now carry active-task coordination context, and installed prepare artifacts include sibling-task warnings. |
| `AGW-071` | done | Harness engineering is now mapped across source and install layers, with quality gates, ownership, and remaining follow-ons split out. |
| `AGW-072` | done | repo-contract-kit 0.4.24 adds `make agent-token-budget`; source docs now define context-economy placement and metric fields preserve required evidence. |
| `AGW-073` | done | repo-contract-kit 0.4.24 adds backlog source discovery, backlog status/check, `agent-next`, and selected-row task-packet scaffolding. |
| `AGW-074` | done | Task-packet and receipt schemas now carry harness metric fields, and the prompt/template asks agents to capture known metrics. |
| `AGW-075` | done | repo-contract-kit 0.4.16 added the AI-first JSON CLI and 0.4.17 made `scripts/repo_contract_kit.py` the stable executable entrypoint with version metadata. |
| `AGW-076` | done | repo-contract-kit 0.4.18 reports deterministic `sidecar_state` metadata under `${XDG_STATE_HOME:-~/.local/state}/repo-contract-kit` without writing target repos during CLI JSON inspection. |
| `AGW-077` | done | repo-contract-kit 0.4.19 adds `update-plan` JSON, makes `update.py` plan-only by default, and keeps mutation behind explicit `--apply`. |
| `AGW-078` | done | `codebase-learning-comments.md` now supports sparse developer learning comments and separate non-developer explanation notes with verification and rejection rules. |
| `AGW-079` | done | repo-contract-kit 0.4.24 adds `make docs-freshness` and wires it into docs-check for links, documented commands, script/schema references, and optional semantic receipts. |
| `AGW-080` | done | repo-contract-kit 0.4.26 adds `make agent-task-closeout` with preview/apply, receipt and clean-worktree gates, active-overlap and unmerged-branch blockers, retention filters, docs, tests, and source dogfood wiring. |
| `AGW-081` | done | agent-workflow-kit 0.2.9 generates `.github/copilot-instructions.md` from `workflows/manifest.json`, lists Copilot as a current adapter, and tests export/check/list behavior. |
| `AGW-082` | done | repo-contract-kit 0.4.29 adds `automation-handoff` / `make agent-automation-handoff` with linked-worktree, original-checkout cleanliness, allowed-path, sidecar patch, receipt, and blocked-run guards; Codex_CodeReview 0.2.9 dogfoods the installed command. |
| `AGW-083` | done | agent-workflow-kit 0.2.15 adds a research `novelty_ledger`, candidate scoring for synthesis/proposals, recurring research prompt gates for low-novelty repeats, generated Codex adapter refreshes, and focused research workflow tests. |
| `AGW-084` | done | `maintainer-queue.md` now reports `Active`, `Needs owner`, `Ready next`, and `Blocked` work from existing local backlog, task-status, receipt, readiness, and automation-handoff signals without adding mutation authority. |
| `AGW-085` | done | repo-contract-kit 0.4.30 adds `agent-preflight` / `agent-doctor` with JSON/text output, strict dirty-state blocking, worktree/task/sidecar summaries, safe recovery recommendations, sidecar receipts, installed Make targets, docs, and regression tests. |
| `AGW-086` | done | repo-contract-kit 0.4.31 makes `agent-task-prepare` dirty-main blockers list dirty entries, tracked/untracked and staged/unstaged counts, recovery commands, and the explicit `ALLOW_DIRTY=1` escape hatch; `TASK_PREPARE_JSON=1` emits machine-readable blocker details. |
| `AGW-087` | done | repo-contract-kit 0.4.32 adds `agent-task-finalize` with `finish`/`block`/`abandon` modes, readiness gating, lifecycle update, task-status and closeout-preview evidence, local finalizer receipts, explicit closeout apply, installed docs, and regression tests. |
| `AGW-088` | done | repo-contract-kit 0.4.33 adds automation-handoff original-checkout baseline capture and compare controls, state hashes, status entries, tracked diff and untracked content hashes, sidecar receipts for baseline/passed/blocked runs, and explicit original-drift override. |
| `AGW-089` | done | agent-workflow-kit 0.2.10 requires closeout evidence in task-packet prompts, templates, schema, and generated Codex adapters: final receipt path, readiness check, lifecycle action, final task-status result, closeout preview, and dirty-state explanation before handoff. |
| `AGW-090` | done | agent-workflow-kit 0.2.16 adds a required task-packet goal-alignment contract with repo goals, affected area contracts, alignment decisions, adaptation-needed flags, and stop conditions before implementation handoff. |
| `AGW-091` | done | repo-contract-kit 0.4.42 adds `goal-check` / `make goal-check` with installed area contracts, changed-file area alignment reports, agent-start and task-ready summaries, task-packet goal-alignment defaults, docs, and regression tests. |
| `AGW-092` | done | repo-contract-kit 0.4.43 adds `agent-context-bundle` / `make agent-context-bundle` with bounded JSON/text sections for dirty state, backlog/next work, task status, docs impact, goal check, token budget, sidecar paths, readiness hints, explicit omissions, docs, and regression tests. |
| `AGW-093` | done | agent-workflow-kit 0.2.17 teaches task-packet, maintainer-queue, verification, and prompt-index guidance to consume compact deterministic reports before broad repo rereads, preserves scoped source fallback and omission evidence, adds deterministic-report-routing fixture controls, refreshes adapters/docs, and validates the prompt regression path. |
| `AGW-094` | done | repo-contract-kit 0.4.44 adds `instruction-diet` / `make agent-instruction-diet` with no-write JSON/text recommendations for budget pressure, route-map drift, duplicated procedures, stale/localizable command detail, installed docs, and regression tests. |
| `AGW-095` | done | repo-contract-kit 0.4.45 adds `DIRTY_PRIMARY_BASELINE=1` for `agent-task-prepare`, recording tracked/untracked dirty-state entries, counts, changed files, HEAD, content-sensitive state hashes, task packet and receipt baselines, readiness/finalize drift blocking, docs, and regression tests. |
| `AGW-096` | done | repo-contract-kit 0.4.46 adds `agent-self-heal` / `make agent-self-heal` with preview-first generated-state recovery, explicit apply, sidecar initialization, stale task metadata and prepare-lock quarantine, tracked-source refusal unless exact generated paths are scoped, unrecognized-untracked reporting, sidecar before/after receipts, docs, and regression tests. |
| `AGW-097` | done | repo-contract-kit 0.4.47 adds `agent-state-ledger` / `make agent-state-ledger` as a read-only local index of checkout dirt, task metadata/worktrees, leases, overlaps, closeout state, finalizer/final receipts, automation handoff/baseline receipts, self-heal/preflight receipts, unresolved blockers/warnings, and deterministic next safe commands with no target or sidecar writes. |
| `AGW-098` | done | agent-workflow-kit 0.2.18 adds required `previous_task_state` and `closeout_required_before_start` task-packet fields, safe-start/refuse-start/blocker-escalation prompt language for task packets, implementers, maintainers, and verification, generated adapter refresh, docs, and ARF-007 regression coverage for unfinished prior task starts. |
| `AGW-099` | done | repo-contract-kit 0.4.48 adds local-only task attribution across prepare, lifecycle, finalizer, task-status, preflight/doctor, receipt scanning, and state-ledger output with owner labels, session/thread/automation ids, run ids, metadata paths, latest receipt provenance, explicit source confidence, installed Make variables, docs, tests, and safer dirty-blocker guidance. |
| `AGW-100` | done | repo-contract-kit 0.5.0 / 79bb855 makes `kit` the public setup/update/doctor surface, keeps workflow source under repo-contract-kit/workflows, preserves root `AGENTS.md`, adds structured update JSON evidence, verifies older-target migrations, and dogfoods this source checkout to the current local kit snapshot. |
| `AGW-101` | done | repo-contract-kit 0.6.0 / 10e7542 adds docs-as-tests manifest v2 with backward-compatible method/path assertions, OpenAPI response-status and schema-property claims, safe local JSON key claims, skipped/unsupported/refused result states, updated docs, tests, validation, and dogfood install evidence. |
| `AGW-053` | done | repo-contract-kit 0.6.2 / be27b2f adds docs-only merge-governance examples that map local `agent-branch-readiness` evidence to GitHub protected branches, required status checks, and merge queue handoff while keeping GitHub API calls, credentials, PR comments, labels, approvals, queue mutation, merge actions, and branch-protection mutation out of scope. |
| `AGW-055` | done | agent-workflow-kit 0.2.29 / 0022da3 adds optional `phase_files` task-packet metadata, prompt/template/docs guidance, implementation and verification phase-scope rules, generated Codex adapters, and contract tests so large reviews and implementations can split into bounded fresh-session phases without replacing task packets or widening scope. |
| `AGW-058` | done | repo-contract-kit 0.6.3 / d4a22f0 adds opt-in Node and Python stack profiles with managed `.agent-workflows/stack-profiles/*.json` command-hint files, `docs/ops/*-stack-profile.md` operator docs, install/update coverage, dummy install evidence, and Codex_CodeReview dogfood metadata while keeping dependency installation, lockfile generation, virtual environment creation, package publishing, and framework scaffolding out of scope. |
| `AGW-059` | done | repo-contract-kit 0.6.4 / 4c829a3 adds managed `docs/planning-adapters.md` examples for Keryx, Obsidian, issue trackers, spreadsheets, and repo backlog mirrors, keeping external systems as priority sources while avoiding external clients, credentials, hosted writes, vault writes, issue mutation, or planning-app behavior. |
| `AGW-060` | done | repo-contract-kit 0.6.5 / d4d7910 adds managed `docs/upgrade-flow.md` plus CLI/options guidance for status, dry-run, conflict review, metadata-only migration, managed update, doctor, and verification, with dummy older-target migration coverage proving customized root `AGENTS.md` is preserved and conflict proposals are written instead of overwriting target instructions. |

New kit CLI backlog from the 2026-06-23 interactivity and smarts spike:

| ID range | Status | Note |
| --- | --- | --- |
| `AGW-107` | done | repo-contract-kit 0.6.6 / 4aea5ac adds `kit command-map --json` and `kit agent-context --json` as a repo-independent command catalogue generated from argparse metadata with parser consistency checks, flags, audience, mutation and target/sidecar write metadata, JSON support, aliases, examples, exit-code notes, output schema pointers, docs pointers, CLI docs, and regression tests. |
| `AGW-108` | done | repo-contract-kit 0.6.7 / c689ebe adds structured parse-error handling with concise did-you-mean text output and a schema-versioned JSON envelope via `--json` or `KIT_AGENT=1` for unknown commands, nested command typos, invalid options, and invalid enum choices, including no-write metadata and regression tests. |
| `AGW-109` | done | repo-contract-kit 0.6.8 / 1d8e8c3 reworks `kit --help`, `kit options`, and `kit help --all` around daily, agent/automation, and maintainer lanes, and text `kit status` now labels running tool version, target install version, target repo version, prompt snapshot, source refs, and safe next commands with regression tests and docs. |
| `AGW-110` | done | repo-contract-kit 0.6.9 / fe25900 adds a global `--no-input` flag, treats `KIT_AGENT=1` as non-interactive and JSON parse-error mode, suppresses guide prompts under scripted or agent mode, and exposes `non_interactive`, `agent_mode`, and `input_contract` metadata on JSON status/error surfaces with docs and regression tests. |
| `AGW-111` | done | repo-contract-kit 0.6.10 / 4dd1123 adds compact human summaries for `kit update --dry-run`, `kit update`, `kit target update`, `kit doctor`, and `kit target doctor`, plus `--verbose` detail mode while preserving JSON output. |
| `AGW-112` | done | repo-contract-kit 0.6.11 / 223da35 adds command-map route taxonomy fields for canonical, alias, agent-only, maintainer, namespace, and compatibility command routes. |
| `AGW-113` | done | repo-contract-kit 0.6.12 / 3b6647b adds command-map `json_contract` metadata with schema pointers, stable payload fields, write metadata fields, explicit non-JSON reasons, `version --json` no-write metadata, README compatibility docs, and regression tests. |
| `AGW-114` | done | repo-contract-kit 0.6.13 / d0cb4fc adds `kit completion bash|zsh|fish`, generated from parser and command-map metadata with command paths, nested subcommands, parser flags, shell choices, README install snippets, command-map metadata, and stdout-only no-write tests. |
| `AGW-115` | done | repo-contract-kit 0.6.14 / 80cd895 adds the TTY-only `kit palette` command with command-map-backed search, exact command preview, `--query`, `--print-command`, non-TTY/no-input/agent disablement, mutation/write metadata, confirmation before printing mutating commands, README docs, and regression tests. |
| `AGW-116` | done | repo-contract-kit 0.6.15 / e6249d6 adds `kit cli-reference` Markdown/JSON generation from command-map metadata, committed `docs/cli-reference.md`, generated docs-as-tests claim metadata, `--check`/`--write` modes, `make docs-freshness` drift gating, README docs, and regression tests. |
| `AGW-117` | done | repo-contract-kit 0.6.16 / 4629aa2 adds fixture-backed CLI UX regression checks for help lanes, parse-error text and JSON, `--no-input`, command-map JSON, compact `doctor` and `update --dry-run` summaries, palette non-TTY fallback, generated CLI-reference freshness, `make cli-ux-fixtures`, and review guidance for intentional wording changes. |
| `AGW-118` | done | repo-contract-kit 0.6.17 / f5ccdfe adds optional stdlib-only `--style auto|plain|pretty` ANSI emphasis for doctor/preflight and update summaries, respects `NO_COLOR`, keeps JSON unstyled, publishes style metadata in command-map CLI metadata, refreshes generated CLI reference docs, and adds regression tests plus fixture plain-output checks. |
| `AGW-119` | done | repo-contract-kit 0.6.18 / 1ac264a adds `kit feedback` as a local sidecar JSONL ledger with repo/tool/target metadata, source, message, context command, optional last error, tags, read-only list/export JSON modes, privacy metadata, no network calls, no upstream submission, and no target-repo writes. |
| `AGW-120` | done | repo-contract-kit 0.6.19 / 351a6a7 adds `kit agent-tool-manifest --json` as a command-map-derived local agent manifest with safe commands, target-writing commands, sidecar-writing commands, schemas, examples, no-input behavior, parser consistency, and explicit no-network/no-hosted-model/no-credential/no-write metadata. |
| `AGW-121` | done | repo-contract-kit 0.6.20 / 0986d6c adds `kit_drift` diagnostics to status and doctor/preflight surfaces, comparing running global tool/local kit version, source ref, and prompt snapshot against target install metadata; classifications cover acceptable, stale, newer-target, unknown, and not-installed states with safe dry-run/update/global-update next commands. |
| `AGW-130` | done | repo-contract-kit 0.6.22 / 33e6a4d adds read-only `task_start_freshness` diagnostics to `make agent-start`, covering global kit state, target install state, repo cleanliness, backlog source, and report-only/dry-run/auto-update-clean/maintenance modes without auto-applying updates. |
| `AGW-131` | done | repo-contract-kit 0.6.23 / c77200f adds story-level task-packet elaboration: schemas require a `story` block and non-empty `non_goals`, direct and backlog packet scaffolds expose `--story-*` overrides with default operator stories, task-worktree packets include story context, and direct/backlog/task-prepare tests plus full kit validation passed. |

Docs review follow-up backlog from the 2026-06-23 source checkout review:

| ID range | Status | Note |
| --- | --- | --- |
| `AGW-122` | done | Source task-packet research handoffs now have a summary rule plus docs-impact benchmark cases proving packet-only edits fail, packet-plus-summary edits pass, and explicit packet-only waivers remain visible. |
| `AGW-123` | done | Legacy source route maps now point new workflow-source edits to `repo-contract-kit/workflows/`, keep this checkout's `workflows/prompts/` as archive material, and make `self-check`/ADR 0002 enforce that distinction. |
| `AGW-124` | done | This dogfood checkout now exposes explicit root `Makefile` wrappers for the active operator docs' installed-kit command surface, documents the target-owned wrapper strategy, and tests documented `make` commands against the root Makefile. |
| `AGW-125` | done | Runtime-adapter, runtime-compatibility, prompt-kit, local tool-agnostic, README, and ADR wording now mark this checkout as legacy/archive material where needed, route current prompt/schema/adapter/task-packet edits to `repo-contract-kit/workflows/`, and keep historical prompt links readable for archive validation. |
| `AGW-126` | done | repo-contract-kit 0.6.24 / 69810e4 adds required task-packet docs-impact fields for documentation surfaces, release metadata, generated docs, contract references, and verification commands; adds CLI overrides; updates prompt/template guidance and generated references; and validates direct, backlog, task-prepare, prompt, schema, and full-suite coverage. |

Version 1 consolidation backlog from the 2026-06-23 owner request:

| ID | Status | Note |
| --- | --- | --- |
| `AGW-127` | done | repo-contract-kit 0.6.21 / `cea21f2` selects the existing `repo-contract-kit` repository as the version 1 workflow-stack identity, adds `docs/version-1-consolidation.md`, links it from the operator docs, adds regression coverage for the single installer/CLI/workflow-source/version-stream invariants, and preserves archive/remote mutation plus the `1.0.0` cut behind explicit release gates. |

Current backlog status on 2026-06-23:

- `124` done
- `0` open
- `0` partial
- `124` total
- no open backlog item is selected by `make agent-next`
- `AGW-126` is complete in repo-contract-kit 0.6.24 with exact docs/release
  metadata task-packet fields, override flags, prompt/template/schema updates,
  generated CLI docs, regression coverage, and full `make test` evidence
- `AGW-124` is complete with target-owned `Makefile` wrappers for documented
  goal/context/ledger/readiness/preflight/self-heal/docs/task/automation/kit
  migration commands, a dogfood strategy note in the operator docs, and a
  documented Make target regression test
- `AGW-123` is complete with updated `AGENTS.md`, `.agent-workflows/README.md`,
  Makefile prompt text, ADR 0002, self-check guidance, and focused
  self-dogfood tests so live workflow-source work routes to
  `repo-contract-kit/workflows/`
- `AGW-122` is complete with a packet-to-summary handoff rule in this summary,
  docs-impact benchmark fixtures for packet-only, packet-plus-summary, and
  explicit-waiver cases, and focused unit coverage for the fixture contract
- `AGW-127` is complete in repo-contract-kit 0.6.21 with a version 1
  consolidation contract, rollback/archive policy, compatibility gate, and
  focused regression tests; validation included full `make test`, docs checks,
  workflow-source check, command-map JSON, and local installer smoke evidence
- `AGW-111` is complete in repo-contract-kit 0.6.10 with compact human
  summaries for `kit update --dry-run`, `kit update`, `kit target update`,
  `kit doctor`, and `kit target doctor`, plus `--verbose` detail mode and
  compatible JSON output
- `AGW-112` is complete in repo-contract-kit 0.6.11 with command-map route
  taxonomy fields for canonical, alias, agent-only, maintainer, namespace, and
  compatibility routes
- `AGW-113` is complete in repo-contract-kit 0.6.12 with command-map
  `json_contract` metadata, schema pointers, stable payload fields, explicit
  non-JSON reasons, `version --json` no-write metadata, README compatibility
  docs, and regression tests
- `AGW-114` is complete in repo-contract-kit 0.6.13 with
  `kit completion bash|zsh|fish`, generated from parser and command-map
  metadata with command paths, nested subcommands, parser flags, shell choices,
  README install snippets, command-map metadata, and stdout-only no-write tests
- `AGW-115` is complete in repo-contract-kit 0.6.14 with TTY-only
  `kit palette` command-map-backed search, exact command previews, `--query`,
  `--print-command`, non-TTY/no-input/agent disablement, mutation/write
  metadata, and confirmation before printing mutating commands
- `AGW-116` is complete in repo-contract-kit 0.6.15 with `kit cli-reference`
  Markdown/JSON generation from command-map metadata, committed
  `docs/cli-reference.md`, generated docs-as-tests claim metadata,
  `--check`/`--write` modes, and `make docs-freshness` drift gating
- `AGW-052` is complete in repo-contract-kit 0.4.54 with
  `branch-readiness` / `make agent-branch-readiness`; it was revalidated under
  repo-contract-kit 0.6.0 before this stale-open backlog row was closed
- `AGW-053` is complete in repo-contract-kit 0.6.2 with docs-only merge
  governance examples and remains intentionally local-only: repo-contract-kit
  does not publish hosted checks, call GitHub, approve, comment, label,
  enqueue/dequeue, merge, edit branch protection, or read credentials
- `AGW-055` is complete in agent-workflow-kit 0.2.29 with optional
  `phase_files` task-packet metadata, source prompt/template/docs guidance,
  implementation and verification phase-scope rules, generated adapters, and
  contract tests
- `AGW-058` is complete in repo-contract-kit 0.6.3 with opt-in Node and Python
  stack profiles, managed local hint JSON, operator docs, install/update tests,
  dummy install evidence, and Codex_CodeReview dogfood to source ref `d4a22f0`
- `AGW-059` is complete in repo-contract-kit 0.6.4 with managed
  `docs/planning-adapters.md` examples for external planning handoffs and
  Codex_CodeReview dogfood to source ref `4c829a3`
- `AGW-060` is complete in repo-contract-kit 0.6.5 with managed
  `docs/upgrade-flow.md`, CLI/options guidance, dummy older-target migration
  coverage, and Codex_CodeReview dogfood to source ref `d4d7910`
- `AGW-034` is complete as a research-only spike note in
  `research/agentic-workflow-review/spikes/agw-034-lsp-context-lookup.md`:
  implementation is deferred to an explicit follow-on, deterministic context
  packets and review maps remain the required fallback, and any LSP lookup must
  be local-only, read-only, best-effort, no-install, no-remote-indexing, capped,
  and omission-reporting.
- `AGW-033` is complete in agent-workflow-kit 0.2.20 with
  `workflows/prompts/templates/review-map.md`,
  `schemas/review-map.schema.json`, generated Codex adapters, review
  skill-pack inclusion, and docs that frame review maps as navigation artifacts
  over context-packet or context-bundle evidence rather than source-review
  substitutes.
- `AGW-031` is complete in agent-workflow-kit 0.2.19 with advisory
  comment/docstring drift labels, two-sided evidence requirements, and
  false-positive handling without adding a scanner, blocking CI gate, or
  repo-contract-kit changes.
- docs/code contract follow-ons now include completed docs-impact localization
  (`AGW-018`), docs proposals (`AGW-019`), experimental docs-as-tests
  (`AGW-030`), advisory comment/docstring drift labels (`AGW-031`), and docs
  freshness (`AGW-079`), with `AGW-101` complete for an explicit docs-as-tests
  claim-manifest v2 rather than prose scraping or unsafe example execution
- observability follow-ons now include completed session receipts (`AGW-007`),
  receipt summaries (`AGW-008`), review outcome and effort metrics (`AGW-048`),
  the source trace concept (`AGW-029`), local state ledger (`AGW-097`), and
  thread/session attribution (`AGW-099`)
- PR interface follow-ons now include completed docs-contract PR comments
  (`AGW-022`), spec-only slash-command grammar (`AGW-023`), local changelog
  proposal/check support (`AGW-024`), and local docs-policy explainer support
  (`AGW-025`)
- newest planned dirty-state follow-ons `AGW-098` through `AGW-099` are complete
  and cover closeout-first startup rules plus thread/session attribution
- newest researched isolation follow-on `AGW-070` is now done in
  repo-contract-kit 0.4.28 with `make agent-task-ready`; branch/PR readiness
  aggregate work is complete in `AGW-052`, and hosted merge-governance examples
  are documented in `AGW-053` without adding hosted mutation authority
- packaging boundary remains split: `AGW-081` is complete for the source-side
  Copilot projection, `AGW-012` is complete for install-layer adapter
  selection/update, and `AGW-043` is complete with a runtime compatibility
  matrix that separates generated, planned, manual-only, and
  unsupported/unknown runtime surfaces
- recurring backlog automation now has clean branch-or-patch handoff in
  `AGW-082`, and `AGW-083` adds novelty/carry-forward controls so nightly
  research rejects repeated questions before proposing backlog edits
- maintainer orchestration remains source-prompt work: `AGW-084` is complete
  without adding a repo-contract-kit command, public schema, or installed
  target-repo API
- dirty-state closeout is split into install-layer and source-layer work:
  `AGW-085` is complete in repo-contract-kit 0.4.30, `AGW-086` is complete in
  repo-contract-kit 0.4.31, `AGW-087` is complete in repo-contract-kit 0.4.32,
  `AGW-088` is complete in repo-contract-kit 0.4.33, and `AGW-089` is complete
  in agent-workflow-kit 0.2.10; `AGW-095` is complete in repo-contract-kit
  0.4.45 with dirty-primary task baselines and readiness/finalize drift guards;
  `AGW-096` is complete in repo-contract-kit 0.4.46 with guarded generated-state
  self-heal and sidecar receipts; `AGW-097` is complete in repo-contract-kit
  0.4.47 with a read-only agent-state ledger for receipts, tasks, dirty state,
  and next safe commands; `AGW-098` is complete in agent-workflow-kit 0.2.18
  with closeout-first task-packet startup rules; `AGW-099` is complete in
  repo-contract-kit 0.4.48 with local thread/session/automation attribution for
  task status, preflight, receipts, state ledger, and dirty blockers.

Validated locally on 2026-06-16 for AGW-043 runtime compatibility matrix:

- agent-workflow-kit / Codex_CodeReview: `make docs-check`
- agent-workflow-kit / Codex_CodeReview: `make docs-freshness`
- agent-workflow-kit / Codex_CodeReview: `make docs-lint`
- agent-workflow-kit / Codex_CodeReview: `make docs-build`
- agent-workflow-kit / Codex_CodeReview: `make docs-generate`
- agent-workflow-kit / Codex_CodeReview: `python3 scripts/check_doc_impact.py`
- agent-workflow-kit / Codex_CodeReview: `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
- agent-workflow-kit / Codex_CodeReview: `PYTHONDONTWRITEBYTECODE=1 make validate`
- agent-workflow-kit / Codex_CodeReview: `make version-check`
- agent-workflow-kit / Codex_CodeReview: `make backlog-check`
- agent-workflow-kit / Codex_CodeReview: `make backlog-split-check`
- agent-workflow-kit / Codex_CodeReview: `git diff --check`

Validated locally on 2026-06-15 for backlog reconciliation and maintainer
orchestration pattern review:

- agent-workflow-kit / Codex_CodeReview: CSV parse check for aggregate, split,
  and feature-matrix files
- agent-workflow-kit / Codex_CodeReview: `python3 scripts/split_backlog_by_repo.py --check`
- agent-workflow-kit / Codex_CodeReview: `make backlog-status`
- agent-workflow-kit / Codex_CodeReview: `make backlog-check`
- agent-workflow-kit / Codex_CodeReview: `make agent-next`
- agent-workflow-kit / Codex_CodeReview: `make docs-lint`
- agent-workflow-kit / Codex_CodeReview: `make docs-build`
- agent-workflow-kit / Codex_CodeReview: `make docs-generate`
- agent-workflow-kit / Codex_CodeReview: `python3 scripts/check_doc_impact.py`
- agent-workflow-kit / Codex_CodeReview: `make agent-docs-localize`
- agent-workflow-kit / Codex_CodeReview: `make docs-freshness`
- agent-workflow-kit / Codex_CodeReview: `make agent-verify`
- agent-workflow-kit / Codex_CodeReview: `VERSION_CHECK_ALLOW_UNCHANGED=1 make version-check`
- agent-workflow-kit / Codex_CodeReview: `git diff --check`

Validated locally on 2026-06-11:

- repo-contract-kit: `make test`
- repo-contract-kit: `make docs-check`
- repo-contract-kit: `make version-check`
- repo-contract-kit: `git diff --check`
- agent-workflow-kit / Codex_CodeReview: `make agent-task-closeout TASK_CLOSEOUT_JSON=1`
- agent-workflow-kit / Codex_CodeReview: `make self-check`
- agent-workflow-kit / Codex_CodeReview: `make backlog-split-check`
- agent-workflow-kit / Codex_CodeReview: `make backlog-check`
- agent-workflow-kit / Codex_CodeReview: `make docs-check`
- agent-workflow-kit / Codex_CodeReview: `make version-check`
- agent-workflow-kit / Codex_CodeReview: `make agent-verify`
- agent-workflow-kit / Codex_CodeReview: `make kit-status KIT=/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- agent-workflow-kit / Codex_CodeReview: `git diff --check`

Validated locally on 2026-06-09:

- agent-workflow-kit / Codex_CodeReview: `make prompt-adapters-check`
- agent-workflow-kit / Codex_CodeReview: `make backlog-split-check`
- agent-workflow-kit / Codex_CodeReview: `make self-check`
- agent-workflow-kit / Codex_CodeReview: `make docs-check`
- agent-workflow-kit / Codex_CodeReview: `make agent-docs-lint`
- agent-workflow-kit / Codex_CodeReview: `make agent-token-budget`
- agent-workflow-kit / Codex_CodeReview: `make validate`
- agent-workflow-kit / Codex_CodeReview: `make agent-verify`
- agent-workflow-kit / Codex_CodeReview: `make backlog-check`
- agent-workflow-kit / Codex_CodeReview: `make agent-next`
- agent-workflow-kit / Codex_CodeReview: `make kit-status KIT=/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- agent-workflow-kit / Codex_CodeReview: `git diff --check`
- repo-contract-kit: `make test`
- repo-contract-kit: `make docs-check`
- repo-contract-kit: `make version-check`
- repo-contract-kit: `git diff --check`

Validated locally on 2026-05-29:

- agent-workflow-kit / Codex_CodeReview: `python3 scripts/split_backlog_by_repo.py --check`
- agent-workflow-kit / Codex_CodeReview: `make agent-docs-localize`
- agent-workflow-kit / Codex_CodeReview: `python3 scripts/check_doc_impact.py`
- agent-workflow-kit / Codex_CodeReview: `make docs-lint`
- agent-workflow-kit / Codex_CodeReview: `make docs-build`
- agent-workflow-kit / Codex_CodeReview: `make docs-generate`
- agent-workflow-kit / Codex_CodeReview: `make version-check`
- agent-workflow-kit / Codex_CodeReview: `make agent-verify`
- agent-workflow-kit / Codex_CodeReview: `git diff --check`

Validated locally on 2026-05-28:

- agent-workflow-kit / Codex_CodeReview: `make kit-update KIT=/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- agent-workflow-kit / Codex_CodeReview: `make kit-status KIT=/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- agent-workflow-kit / Codex_CodeReview: `make kit-explain KIT=/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- agent-workflow-kit / Codex_CodeReview: `make agent-docs-localize`
- agent-workflow-kit / Codex_CodeReview: `make agent-verify`
- agent-workflow-kit / Codex_CodeReview: `git diff --check`

Validated locally on 2026-05-26:

- agent-workflow-kit / Codex_CodeReview: `make kit-update KIT=/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- agent-workflow-kit / Codex_CodeReview: `make kit-status KIT=/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- repo-contract-kit: `make test`
- repo-contract-kit: `make docs-check`
- repo-contract-kit: `make version-check`

Validated locally on 2026-05-21:

- agent-workflow-kit: `make agent-start`
- agent-workflow-kit: `make agent-task-status`
- agent-workflow-kit: `make agent-verify`
- agent-workflow-kit: `make agent-docs-localize`
- agent-workflow-kit: `python3 scripts/split_backlog_by_repo.py`
- agent-workflow-kit: `AGW-071` task packet created under `.agent-workflows/tasks/agw-071/`

Validated locally on 2026-05-14:

- agent-workflow-kit: `python3 -m unittest discover -s tests`
- agent-workflow-kit: `make validate`
- repo-contract-kit: `python3 -m unittest discover -s tests`
- repo-contract-kit: throwaway target install with `make agent-docs-lint`

## Source Caveats

- X and Reddit results are time-sensitive, personalized, and anecdotal unless backed by official docs or source code.
- Google Scholar direct access hit automated-query blocking; Scholar entries are exact-title search URLs and should be refreshed before citation-quality use.
- Vendor docs and product pages were treated as product claims, not independent validation.
- GitHub stars/releases and public activity snapshots can drift quickly.
