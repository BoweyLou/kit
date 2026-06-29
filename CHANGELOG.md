# Changelog

## 0.6.35 - 2026-06-29

- Add read-only `kit target dirty-report` for enrolled repos so operators can
  see dirty targets before global maintenance.
- Make `kit update --all --dry-run` classify dirty targets before running
  update plans, avoiding stale metadata/profile failures from repos that need
  human cleanup first.
- Document the dirty-report step in batch target update workflows.

## 0.6.34 - 2026-06-29

- Make `kit worktree audit --root <repo>` and `kit worktree prune --root <repo>`
  include the repo's Git-linked sibling worktrees under disposable
  `agent-worktrees` paths, while preserving parent-directory scans.
- Add JSON discovery-source diagnostics for worktree audit and prune summaries
  and entries.
- Document exact repo-root worktree cleanup examples.

## 0.6.33 - 2026-06-29

- Add `kit target import` and `kit target list` so global batch updates can be
  seeded with primary repos while excluding agent-worktree and archive paths by
  default.
- Add `kit worktree audit` and `kit worktree prune` to inspect disposable
  agent worktrees and remove only clean linked worktrees with explicit
  `--apply`.

## 0.6.32 - 2026-06-29

- Add a local enrolled-target registry populated by successful `kit setup` and
  `kit update` runs.
- Add `kit target update-all` and the short `kit update --all` route, with
  dry-run default and `--apply` required for batch target writes.
- Skip dirty, missing, or no-longer-enrolled targets during batch apply and
  report per-target statuses in JSON output.
- Add `kit target prune-missing` so stale missing enrolled-target registry
  entries can be cleaned without writing target repos.

## 0.6.31 - 2026-06-29

- Split real Git worktree state from kit-managed template/proposal state in
  status and closeout-plan JSON/text so agents stop treating pending kit
  proposals as ordinary dirty source files.
- Add setup closeout guidance and closeout-plan blockers for pending
  managed-file proposals.
- Block dirty-primary task prep when untracked files overlap the declared task
  scope, and parse whitespace-separated scope values as separate paths.

## 0.6.30 - 2026-06-28

- Add read-only `kit closeout-plan`, translating dirty checkout, task,
  receipt, and closeout-preview evidence into `can_claim_done`,
  `completion_state`, `claim_blockers`, and a concrete `next_action`.
- Document the final handoff rule for agents: run `kit closeout-plan --json`
  after validation and avoid “done” wording when closeout blockers remain.
- Add regression coverage for clean closeout, dirty primary checkout, active
  task state, and terminal tasks missing final receipts.

## 0.6.29 - 2026-06-28

- Let `kit start` opportunistically apply already-local, local-safe managed-file
  and kit-metadata updates for installed target repos, while keeping
  remote/global updates explicit through `kit update --global`.
- Add `kit start --no-update` and `--update-policy check-only|local-safe`, plus
  a structured `local_update` payload that reports checked/applied state,
  planned and written paths, blockers, versions, and next commands.
- Update agent/human docs, installed templates, generated CLI reference, UX
  fixtures, and regression coverage for no-write startup, check-only planning,
  local-safe apply, and customized-file conflict blocking.

## 0.6.28 - 2026-06-27

- Make `kit start` the canonical journey front door with a `--lite` shorthand,
  additive `repo_role` payload field, and a maintainer-source journey for the
  running kit source checkout.
- Add guide and agent manifest journey metadata so agents can distinguish
  `kit start --json`, installed `make agent-*` packet/context lanes, command-map
  metadata, and direct source-checkout fallbacks.
- Harden Codex thread mining with private local artifact permissions, broader
  redaction, aggregate-only JSON stdout by default, current-era/kit filters, and
  split command counts for kit, make, shell, and agent tool calls.

## 0.6.27 - 2026-06-26

- Add `scripts/mine_codex_threads.py`, a local maintainer mining pipeline for
  classifying Codex thread history into CLI routes, journeys, friction markers,
  outcomes, and recommended follow-up actions without committing raw thread
  text.
- Add fixture coverage for session/history/archive parsing, route and journey
  classification, blocked/error detection, and redaction guarantees.
- Add the generated aggregate `docs/cli-journey-research.md` report and link it
  from maintainer-facing review docs.

## 0.6.26 - 2026-06-26

- Add `kit start` as a read-only human and agent entrypoint that inspects the
  current repo, reports the selected journey and harness mode, and returns next
  commands for fresh setup, dirty work-in-progress, or ready maintenance flows.
- Promote `kit start` in the README, human guide, agent guide, generated CLI
  reference, and regression tests so users and agents have one obvious first
  command before choosing setup, update, task-packet, or verify routes.
- Add a maintainer CLI/function review with prioritized follow-up refactors for
  the command router, journey policy, JSON schemas, aliases, and UX fixtures.

## 0.6.25 - 2026-06-24

- Add the `lite` install preset plus managed lite-mode and sidecar-retention
  guidance for small repos and low-risk local work without installing prompt
  packs or target versioning files.
- Add deterministic harness mode selection with `kit mode-check --json`,
  `--harness-mode` task-packet/verify integration, compact lite task notes,
  read-only calibration and retention reports, generated CLI docs, and
  regression coverage for lite, standard, and release-gated routing.

## 0.6.24 - 2026-06-23

- Require task packets to name exact documentation surfaces, release metadata,
  generated docs, schema/API/config references, and docs validation commands
  before implementation handoff.
- Add `--docs-surface`, `--release-metadata`, `--generated-doc`,
  `--contract-reference`, and `--docs-validation-command` task-packet overrides,
  with default coverage for direct, backlog, and task-worktree packets plus
  prompt/schema regression tests.

## 0.6.23 - 2026-06-23

- Require executable task packets to include story context and explicit
  non-goals, while keeping raw backlog rows compact.
- Add `--story-*` CLI overrides, backlog-derived default operator stories,
  task-worktree packet story fields, generated CLI docs, and regression coverage
  for direct, backlog, and task-prepare packet generation.

## 0.6.22 - 2026-06-23

- Add task-start freshness diagnostics to `make agent-start`, reporting global
  kit metadata, target install metadata, repo cleanliness, backlog source, and
  safe update modes in the startup packet and brief without applying target or
  global updates.
- Document the report-only default, dry-run preview, gated clean-checkout target
  update, and explicit maintenance/global-update policies, with regression
  coverage for stale target installs.

## 0.6.21 - 2026-06-23

- Add the version 1 consolidation contract naming `repo-contract-kit` as the
  single workflow-stack repository identity, documenting the old source-checkout
  archive policy, compatibility requirements, release gate, and rollback path.
- Add regression coverage that the docs, installer defaults, workflow source,
  CLI entrypoint, and single `VERSION` / `CHANGELOG.md` stream remain aligned
  before a `1.0.0` cut.

## 0.6.20 - 2026-06-23

- Add `kit_drift` diagnostics to status and doctor surfaces, comparing the
  running global tool with the target install receipt, source refs, and prompt
  snapshot, then classifying acceptable, stale, newer-target, unknown, or
  not-installed states with safe dry-run/update repair commands.

## 0.6.19 - 2026-06-23

- Add `kit agent-tool-manifest --json` as a command-map-derived local agent
  manifest that separates safe, target-writing, and sidecar-writing commands,
  schemas, examples, and no-input behavior without network, hosted-model,
  credential, target-repo, or sidecar writes.

## 0.6.18 - 2026-06-23

- Add `kit feedback` as a local sidecar JSONL ledger for CLI friction notes,
  including repo/tool/target metadata, command context, optional last error,
  tags, JSON export/list modes, and explicit no-network/no-upstream privacy
  metadata.

## 0.6.17 - 2026-06-23

- Add optional stdlib-only human summary styling with `--style auto|plain|pretty`
  for doctor and update summary surfaces, with `NO_COLOR` support and plain JSON
  output preserved.

## 0.6.16 - 2026-06-23

- Add fixture-backed CLI UX regression checks for top-level help, parse errors,
  no-input and agent-mode behavior, command-map JSON, compact update and doctor
  summaries, palette non-TTY fallback, and generated CLI reference freshness.
- Add `make cli-ux-fixtures` and review guidance for intentional CLI wording or
  structure changes.

## 0.6.15 - 2026-06-23

- Add `kit cli-reference` to generate Markdown or JSON from `kit command-map`,
  publish docs-as-tests claim metadata, write or check `docs/cli-reference.md`,
  and fail `make docs-freshness` when the generated CLI reference drifts.

## 0.6.14 - 2026-06-23

- Add the TTY-only `kit palette` command for command-map-backed search, exact
  command previews, `--query` filtering, `--print-command`, non-interactive and
  agent-mode disablement, and confirmation before printing mutating commands.

## 0.6.13 - 2026-06-23

- Add `kit completion bash|zsh|fish`, generated from parser and command-map
  metadata with command paths, nested subcommands, parser flags, docs pointers,
  and regression tests proving the command writes only to stdout.

## 0.6.12 - 2026-06-23

- Add command-map JSON contract metadata with schema pointers, stable payload
  field promises, write-metadata fields, and explicit non-JSON reasons for
  namespace or text-only routes.
- Add read-only no-write metadata to `kit version --json` so the agent-facing
  version payload matches the documented JSON contract.

## 0.6.11 - 2026-06-23

- Add command-map route taxonomy fields for canonical, alias, agent-only,
  maintainer, namespace, and compatibility-oriented command routes, including
  canonical command pointers, alias groups, and route notes for ambiguous
  setup/install/target and doctor/preflight surfaces.

## 0.6.10 - 2026-06-23

- Add compact human summaries for `kit update --dry-run`, `kit update`,
  `kit target update`, `kit doctor`, and `kit target doctor`, leading with
  blockers, conflict counts, proposal paths, write guarantees, and next
  commands while preserving JSON output for agents.
- Add `--verbose` to update commands so operators can show raw updater detail
  after the compact summary when needed.

## 0.6.9 - 2026-06-23

- Add a global `--no-input` flag and `KIT_AGENT=1` non-interactive contract,
  with prompt suppression for guide/help paths and `non_interactive`,
  `agent_mode`, and `input_contract` metadata on JSON status/error surfaces.

## 0.6.8 - 2026-06-23

- Rework `kit --help`, `kit options`, and text `kit status` around human
  scenario lanes, explicit running-tool versus target-install version roles,
  prompt/source ref labels, and safe next-command guidance.

## 0.6.7 - 2026-06-23

- Add structured parse-error handling with concise text suggestions and a
  `KIT_AGENT=1` / `--json` envelope for unknown commands, invalid flags, and
  invalid enum values before any target repo lookup or writes occur.

## 0.6.6 - 2026-06-23

- Add `kit command-map --json` and the `kit agent-context --json` alias for a
  schema-versioned command catalogue generated from argparse metadata and
  annotated with mutation class, sidecar write behavior, aliases, examples,
  output schema pointers, and docs pointers.

## 0.6.5 - 2026-06-22

- Add an installed guided upgrade flow covering status, dry-run, conflict
  review, metadata-only migration, managed update, doctor, and verification,
  with regression coverage for older target metadata preserving customized root
  `AGENTS.md`.

## 0.6.4 - 2026-06-22

- Add docs-only planning adapter examples for Keryx, Obsidian, issue trackers,
  spreadsheets, and repo backlog mirrors, keeping external systems as priority
  sources while task packets remain the bounded local implementation handoff.

## 0.6.3 - 2026-06-22

- Add opt-in Node and Python stack profiles with managed local command-hint
  JSON files and operator docs while keeping dependency installation, lockfile
  generation, virtual environment creation, package publishing, and framework
  scaffolding out of scope.

## 0.6.2 - 2026-06-22

- Add docs-only merge-governance examples that map local
  `agent-branch-readiness` evidence to GitHub branch protection, required
  status checks, and merge queue handoff without adding GitHub API calls,
  credential handling, PR comments, labels, approvals, queue mutation, or
  branch-protection mutation.

## 0.6.1 - 2026-06-22

- Make top-level `kit update --json` apply managed updates by default, matching
  `kit update` and `kit target update --json`; `--dry-run` and `update-plan`
  remain non-mutating.

## 0.6.0 - 2026-06-22

- Expand the opt-in `docs-as-tests` profile to manifest v2 while preserving
  existing schema v1 `openapi_operation_exists` assertions.
- Add explicit local claim checks for OpenAPI response statuses, OpenAPI schema
  properties, and JSON config/reference keys, with passed, failed, skipped,
  unsupported, and refused results.
- Keep docs-as-tests local-read-only: unsafe inputs, unsupported claim kinds,
  network URLs, missing artifacts, and ambiguous selectors are refused without
  target writes, service startup, prose scraping, or hosted-model calls.

## 0.5.0 - 2026-06-18

- Make `kit` the default global launcher installed by `install.sh`, with
  `KIT_COMMAND` as the new command-name override and
  `REPO_CONTRACT_KIT_COMMAND` retained as a one-release compatibility fallback.
- Add the guided `kit` no-args dashboard plus `kit setup`, `kit options`,
  `kit doctor`, and `kit update --global` so humans can manage the tool and
  target repos without memorizing the full advanced command tree.
- Keep existing advanced commands available through the same Python entrypoint
  while reframing README, rollout, source, and target-template guidance around
  the new public `kit` command.

## 0.4.60 - 2026-06-18

- Make the global installer default to the single public `repo-contract-kit`
  surface by skipping the companion `agent-workflow-kit` source checkout unless
  maintainers opt in with `--with-workflow`.
- Keep `repo-contract-kit self update` quiet for missing optional workflow
  source checkouts, while still updating them when explicitly installed.
- Reframe stack and rollout docs around one global CLI plus per-repo
  `target add/status/update/doctor` management, with workflow-source details
  owned by this repo and legacy external workflow checkouts marked as
  maintainer-only compatibility.
- Import canonical workflow prompt and schema source under `workflows/`, rename
  new install provenance to `workflow-source`, and keep legacy
  `agent-workflow-kit` receipt parsing for older installs.
- Add `make workflow-source-check` and `make workflow-source-export` so
  in-repo workflow source edits refresh the installed target templates before
  release.
- Update installed target templates, startup packets, `workflow-help`, and
  `kit-explain` so the global `repo-contract-kit target ...` commands are the
  primary maintenance path and local `KIT=/path` flows are fallback or
  maintainer-only.
- Demote installed `kit-update-stack` and `kit-refresh-stack` to explicit
  compatibility shims that require `STACK_UPDATE_COMPAT=1`, so ordinary target
  repos do not accidentally enter the old two-repo update flow.
- Add `repo-contract-kit target doctor` as a global non-mutating diagnostic alias
  for the existing target-repo doctor checks.
- Rename target-facing status/brief text from the source repo name to the
  generic workflow prompt snapshot label while preserving provenance metadata.
- Keep default installer and `self status` output focused on `repo-contract-kit`;
  optional workflow-source details appear only when maintainers opt in.

## 0.4.59 - 2026-06-18

- Treat ADRs, audits, archives, and changelog history as historical
  docs-freshness paths for documented `make`, script, and schema references,
  while keeping local link checks active.
- Add `doc-contract.json` `docs_freshness` scope controls for historical,
  extra-historical, and fully excluded Markdown paths, plus installed docs and
  regression coverage.

## 0.4.58 - 2026-06-16

- Add `repo-contract-kit target repair-source-clone`, a preview-first cleanup
  command for accidental nested `repo-contract-kit` or `agent-workflow-kit`
  source checkouts inside target repos.
- Require `--apply` before removing nested source directories, block unrelated
  dirty target files, refuse root source-checkout deletion, and report
  `target_repo_writes` plus next target-mode commands for automation.

## 0.4.57 - 2026-06-16

- Extend the global `install.sh` bootstrap to provision both source checkouts:
  `repo-contract-kit` for the global CLI and `agent-workflow-kit` for companion
  workflow-source maintenance outside target repos.
- Include the workflow source path in the generated launcher and `self status`,
  and have `self update` refresh both global checkouts while target repos still
  consume only vendored snapshots through explicit `target update`.

## 0.4.56 - 2026-06-16

- Add `repo-contract-kit self status` and `repo-contract-kit self update` for
  inspecting and refreshing the globally cached tool checkout.
- Add `repo-contract-kit target status` and `repo-contract-kit target update` so
  each enrolled repo can be inspected or safely updated from the global tool
  checkout without requiring Makefile `KIT=...` paths.

## 0.4.55 - 2026-06-16

- Add `install.sh`, a machine-level bootstrap that caches `repo-contract-kit`
  outside target repos and writes a global `repo-contract-kit` launcher.
- Add `repo-contract-kit target add` as the simple target-enrollment command for
  use inside each repo, while preserving the explicit `install --repo` wrapper
  and source-checkout installer path.

## 0.4.54 - 2026-06-16

- Add `branch-readiness` / `make agent-branch-readiness`, a no-write
  branch-or-PR readiness aggregate for local git state, base/head refs,
  docs-impact and `No docs needed:` waiver state, changelog/version evidence,
  task readiness references, task-status hazards, optional CI/check JSON,
  receipt validation, and review-disposition input.
- Report top-level `target_repo_writes=false`, `sidecar_writes=false`, and
  `network_calls=false`, block failing required checks or invalid local
  evidence, and document that hosted merge-governance examples remain deferred
  to AGW-053.

## 0.4.53 - 2026-06-15

- Add the opt-in `private-context` profile with managed `.agent-context/`
  README/example templates for shareable project context, user preference
  context, and private local context.
- Install a managed `.agent-context/.gitignore` that tracks only README/example
  guidance and ignores real local context files by default; document privacy
  warnings and keep the profile out of default, minimal, learning, test-first,
  and agentic presets.

## 0.4.52 - 2026-06-15

- Add the experimental `docs-as-tests` profile with
  `.agent-workflows/docs-as-tests.json`, `docs/ops/docs-as-tests.md`, and a
  local `openapi_operation_exists` assertion for declared API documentation
  checks against JSON OpenAPI specs.
- Expose `check_docs_as_tests.py`, `repo_contract_kit.py docs-as-tests`, and
  installed `make docs-as-tests` without adding the profile to default,
  minimal, or agentic presets; the checker reports refusals for unsafe,
  unsupported, missing, ambiguous, or network-like inputs and keeps
  `docs-check` unchanged.

## 0.4.51 - 2026-06-15

- Add `docs-explain` / `make agent-docs-explain`, a deterministic local
  README/docs/policy explainer that returns cited source paths, headings,
  snippets, and a ready local prompt before docs waivers or docs-patch requests.
- Keep the explainer read-only by default: it does not write target files,
  sidecar files, `VERSION`, or `CHANGELOG.md`, and it does not call hosted
  models or the network; check mode can fail when no matching local docs are
  found.

## 0.4.50 - 2026-06-15

- Add a deterministic `changelog-update` helper plus installed
  `make agent-changelog-update` target to propose or check release-note work
  from docs-impact context without writing target-owned `VERSION` or
  `CHANGELOG.md`.
- Report target version/changelog state, candidate changelog text, safe
  validation commands, and explicit write-only follow-up commands for accepted
  release scope.

## 0.4.49 - 2026-06-15

- Record `profile_config_schema_version` in install receipts and managed
  manifests so installed repos can detect missing, outdated, blocked, or
  current profile/config metadata schema state.
- Add a plan-first `migrate-profile-config` update action plus explicit
  metadata-only apply paths through `update.py --apply --metadata-only`,
  `repo_contract_kit.py migrate-config`, and installed
  `make kit-migrate-config`, preserving target-owned files and customized
  managed-file conflict baselines.

## 0.4.48 - 2026-06-15

- Add local-only task attribution across prepare, lifecycle, finalizer, task
  status, preflight/doctor, and state-ledger output, including optional owner
  label, thread id, automation id, run id, metadata path, latest receipt
  provenance, and explicit `metadata`, `receipt`, `inferred`, or `unknown`
  source confidence.
- Install `TASK_OWNER_LABEL`, `TASK_THREAD_ID`, and `TASK_AUTOMATION_ID` Make
  variables while preserving existing `TASK_OWNER` and `TASK_SESSION_ID`
  compatibility, and document how agents should treat missing attribution as
  non-authoritative.

## 0.4.47 - 2026-06-15

- Add `agent-state-ledger` / `make agent-state-ledger` as a read-only local
  index across checkout dirty state, task metadata/worktrees, leases, overlaps,
  closeout state, sidecar receipt categories, automation handoff/baseline
  receipts, self-heal receipts, finalizer receipts, and linked final receipts.
- Report unresolved blockers and warnings with deterministic next safe commands
  while explicitly returning `target_repo_writes=false` and
  `sidecar_writes=false`; the ledger does not clean, close out, finalize, hand
  off, self-heal, or write receipts.

## 0.4.46 - 2026-06-15

- Add `agent-self-heal` / `make agent-self-heal` as a preview-first recovery
  command for sidecar initialization and stale generated task-state quarantine.
- Require explicit apply mode for writes, refuse unrelated tracked source
  changes, report unrecognized untracked files without deleting them, and write
  sidecar before/after receipts with target and sidecar write paths.

## 0.4.45 - 2026-06-15

- Add dirty-primary baseline mode to `agent-task-prepare` via
  `DIRTY_PRIMARY_BASELINE=1`, recording primary checkout status entries,
  counts, changed files, HEAD, content-sensitive hashes, and deterministic
  state hash in task metadata, task packets, and receipt templates.
- Make `agent-task-ready` and `agent-task-finalize` compare the current primary
  checkout against the stored dirty baseline and block when the primary changed
  after preparation; keep `ALLOW_DIRTY=1` as a legacy alias for the same guarded
  baseline mode.

## 0.4.44 - 2026-06-15

- Add `instruction-diet` / `make agent-instruction-diet` to emit a no-write
  JSON/text audit of agent-facing instruction files with offload
  recommendations for budget pressure, route-map drift, duplicated procedure,
  and stale or localizable command detail.
- Document the audit as a proposal surface rather than an automatic pruning
  command, preserving target repo files until a human reviews the suggested
  offload targets.

## 0.4.43 - 2026-06-15

- Add `agent-context-bundle` / `make agent-context-bundle` to compose dirty
  state, backlog/next work, task status, docs impact, goal check, token budget,
  sidecar paths, and readiness hints into a bounded JSON/text startup or
  handoff report.
- Record explicit omissions when compact bundle sections are truncated so
  agents can prefer deterministic context without hiding missing evidence.

## 0.4.42 - 2026-06-15

- Add deterministic `goal-check` / `make goal-check` reporting for changed
  files against `.agent-workflows/area-contracts.json`, with JSON/text output
  for `aligned`, `extends`, `conflict`, and explicit `unknown` path states.
- Install area-contract config/schema templates, include compact goal-check
  summaries in `agent-start`, add goal-check status to `agent-task-ready`, and
  populate `goal_alignment` defaults in generated task packets.

## 0.4.41 - 2026-06-15

- Install research novelty-ledger and candidate-score templates so
  `agent-research-plan` and `agent-research-synthesize` produce artifacts that
  match the source research schemas.
- Refresh vendored research prompts and installed research schemas with the
  recurring-research novelty and carry-forward contract.

## 0.4.40 - 2026-06-15

- Extend strict receipt validation for `learning-comments` runs so they must
  prove `scope.behavior_change=false` with structured comment-only or
  explanation-note evidence.
- Install `evidence.comment_only_verification` in session receipt schemas and
  preserve behavior-neutral no-source explanation-note runs when they record an
  explicit no-source-edit reason.

## 0.4.39 - 2026-06-15

- Install `docs/ops/slash-command-grammar.md`, a specification-only PR command
  grammar for `/docs-impact`, `/waive-docs`, `/review-docs`, `/add-docs`, and
  `/update-changelog`.
- Document command intent, allowed arguments, permission boundaries,
  receipt/comment behavior, and rejection cases without adding command
  execution, bot mutation, external API calls, or hosted automation behavior.

## 0.4.38 - 2026-06-15

- Install `.github/workflows/docs-contract-comment.yml`, an optional
  `pull_request_target` adapter that runs docs-impact on PR changed filenames
  using base-repo policy files and upserts one docs-contract status comment.
- Add `scripts/render_docs_contract_comment.py` to render deterministic PR
  comment Markdown with status, policy links, category details, and next
  actions.

## 0.4.37 - 2026-06-15

- Add `onboarding-pr` to generate Renovate-style branch, install, validation,
  commit, push, and manual PR instructions for installing repo-contract-kit into
  an existing repo without mutating the target checkout.
- Support `onboarding-pr --write-sidecar` to store deterministic JSON and
  Markdown review bundles under the repo sidecar while preserving
  `target_repo_writes.performed: false`.

## 0.4.36 - 2026-06-15

- Add `docs-propose` / `make agent-docs-propose` to generate reviewable docs
  proposal JSON, Markdown, and patch scaffold artifacts under the repo sidecar
  without modifying target files.
- Extend sidecar state with `docs-patch-proposals/` and cover the proposal mode
  with CLI and installer regression tests.

## 0.4.35 - 2026-06-15

- Add explicit runtime adapter selection for `claude-code` and `github-copilot`
  through install, update, update-plan, wrapper CLI, and installed Make targets.
- Install managed thin adapters at `CLAUDE.md` and
  `.github/copilot-instructions.md`, record selected adapters in receipts and
  manifests, include them in `kit-status`, and preserve customized adapters with
  normal update conflict reports.

## 0.4.34 - 2026-06-15

- Add SARIF output for docs-contract findings through
  `check_doc_impact.py --format sarif` and
  `repo_contract_kit.py doc-impact --format sarif`, with regression coverage.
- Keep agent-safety SARIF covered by tests and have the read-only workflow
  produce both `docs-impact.sarif` and `agent-docs-lint.sarif`.

## 0.4.33 - 2026-06-15

- Add `agent-automation-handoff` original-checkout baseline capture and compare
  controls so recurring automation can preserve pre-existing live dirt while
  still blocking original-checkout mutations introduced during a run.
- Record original checkout state hashes, status entries, tracked diff hashes,
  untracked content hashes, baseline comparison details, and explicit drift
  overrides in sidecar handoff receipts for passed and blocked runs.

## 0.4.32 - 2026-06-15

- Add `agent-task-finalize` to close prepared task packets through one
  readiness, lifecycle, task-status, closeout-preview, and finalizer-receipt
  flow, with `finish`, `block`, and `abandon` terminal modes.
- Install `make agent-task-finalize` with JSON, readiness-skip, base-ref,
  owner/session, and explicit closeout-apply controls so agents can leave a
  durable task-state receipt without implicitly removing sibling worktrees.

## 0.4.31 - 2026-06-15

- Make `agent-task-prepare` dirty-check failures actionable by listing dirty
  entries, tracked/untracked and staged/unstaged counts, and concrete recovery
  commands including `agent-preflight`, task status, closeout, and the explicit
  `ALLOW_DIRTY=1` escape hatch.
- Add `TASK_PREPARE_JSON=1` / `--json` blocker output so automation and agents
  can parse dirty-check failures instead of repeating vague dirty-worktree text.

## 0.4.30 - 2026-06-15

- Add `agent-preflight` / `agent-doctor` to diagnose dirty-state startup
  blockers, registered worktrees, task metadata, sidecar availability, and safe
  recovery commands before write-capable work starts.
- Install `make agent-preflight` and `make agent-doctor` with JSON, strict, and
  sidecar-receipt controls so agents can fail closed or leave a durable
  diagnostic receipt without writing target repo files.

## 0.4.29 - 2026-06-13

- Add `automation-handoff` to preserve recurring automation backlog/research
  edits as sidecar patch and receipt artifacts without writing the original
  checkout.
- Install `make agent-automation-handoff` with linked-worktree, original
  checkout cleanliness, allowed-path, and blocked-receipt guards so unattended
  runs fail closed before dirtying live checkouts or losing accepted backlog
  edits.
- Reuse the standalone review-risk classifier from `agent_start.py` so startup
  packets and `scripts/classify_review_risk.py` share one routing source.

## 0.4.28 - 2026-06-13

- Add installed `make agent-task-ready` as a local handoff gate for prepared
  task worktrees, with JSON/text output, declared-scope drift checks, base
  branch freshness checks, strict receipt and docs-impact validation, and
  active-task overlap blocking before PR update or merge handoff.
- Install `scripts/agent_task_ready.py`, update installed workflow and harness
  docs, and add regression coverage for in-scope success, scope drift,
  stale-base, and invalid-receipt cases.

## 0.4.27 - 2026-06-11

- Add installed `make kit-update-stack` and `make kit-refresh-stack` so an
  agent running in a target repo can update that repo and the local
  `agent-workflow-kit` / `Codex_CodeReview` dogfood checkout from one command.
- Add `scripts/kit_update_stack.py` with local checkout discovery, optional kit
  fast-forward refresh, text/JSON output, docs, and regression coverage for
  updating both repos.

## 0.4.26 - 2026-06-11

- Add installed `make agent-task-closeout` for preview-first cleanup of finished
  sibling task worktrees, with clean-status, terminal-metadata,
  durable-receipt, known-scope, active-overlap, default-pool, and merged-branch
  gates before any removal.
- Add closeout retention controls, explicit apply mode, metadata pruning after
  successful `git worktree remove`, installed docs, and regression coverage for
  dry-run, applied removal, blocked candidates, and keep-count behavior.

## 0.4.25 - 2026-06-10

- Make `agent-start` use the portable backlog source contract so startup
  packets report the selected Markdown or CSV backlog source instead of only
  checking `docs/backlog.md`.
- Refresh installed workflow README and review-contract templates with the
  newer backlog, docs-freshness, task lifecycle, and token-budget command
  surfaces without treating optional backlog candidate paths as required files.

## 0.4.24 - 2026-06-09

- Add backlog source discovery with `backlog-status`, `backlog-check`,
  `agent-next`, and `agent-task-packet-from-backlog` so installed repos can
  standardize backlog-to-task handoff without adopting a backlog app.
- Add task lifecycle metadata and commands for finish, block, abandon,
  heartbeat, receipt linking, and closed-task pruning, including owner/session
  fields, run ids, leases, sibling-task context, and strict status warnings.
- Add docs-freshness checks for local Markdown links, documented make targets,
  script references, schema references, and optional semantic review receipts.
- Add receipt behavior-change evidence checks, optional harness metrics fields,
  and token-budget reporting for agent-facing context files.

## 0.4.23 - 2026-05-29

- Add installed `scripts/_agent_scope.py` so `agent_task_prepare.py` and
  `agent_task_status.py` share task-scope parsing and overlap checks instead
  of carrying copy-pasted helpers.
- Add regression coverage proving the task prepare/status scripts import the
  shared scope helpers.

## 0.4.22 - 2026-05-29

- Add explicit sidecar setup commands to update plans and update reports so an
  updating agent sees `sidecar-init` and `--write-sidecar` guidance immediately
  after moving to a sidecar-capable kit.
- Document that kit updates do not automatically migrate existing repo-local
  `.agent-workflows/runs/`, `.agent-workflows/tasks/`, or
  `.doc-contract-kit/updates/` artifacts.

## 0.4.21 - 2026-05-29

- Add explicit `sidecar-init` support for creating repo-external agent state
  directories without writing kit files into a target repository.
- Add `--write-sidecar` to `orient`, `review-plan`, `task-packet`, and `verify`
  so agents can store run packets, review plans, task packets, and verify
  receipts under `${XDG_STATE_HOME:-~/.local/state}/repo-contract-kit/`.
- Report `sidecar_writes` separately from `target_repo_writes`, preserving the
  no-target-write contract for exploratory and third-party repo workflows.
- Document sidecar-backed workflow storage and add regression coverage proving
  sidecar artifacts do not create `.agent-workflows/` or `.doc-contract-kit/` in
  target repos.

## 0.4.20 - 2026-05-28

- Accept documented prerelease SemVer values such as `0.3.0-beta.1` in the
  installed `make version-check` path.
- Add regression coverage for prerelease validation, invalid numeric prerelease
  identifiers, and patch bumps from prerelease versions.
- Update the installed versioning docs template so target repos know
  prerelease versions are supported.
- Add upgrade `read_next` guidance to update plans and update reports, and make
  Makefile boundary checks recognize target-owned Makefiles with direct kit
  targets.

## 0.4.19 - 2026-05-27

- Add a plan-first migration/update surface with `update-plan` JSON for
  no-install, sidecar-only, legacy, current, dirty, invalid, customized, and
  missing managed-file states.
- Make `scripts/update.py` non-mutating by default and require `--apply` for
  target repo updates while keeping installed `make kit-update` on the explicit
  apply path.
- Add regression coverage for update planning, sidecar-only detection, invalid
  metadata blockers, dirty target warnings, and dry-run write boundaries.

## 0.4.18 - 2026-05-27

- Add deterministic sidecar state metadata under
  `${XDG_STATE_HOME:-~/.local/state}/repo-contract-kit/` to read-only CLI JSON
  so agents can locate non-installed run state outside target repositories.
- Report `target_repo_writes` and `sidecar_state` from non-mutating CLI
  commands while keeping orient/status/review-plan/verify/doc-impact/task-packet
  from creating target repo or sidecar directories.
- Document the non-invasive sidecar behavior and add regression coverage for
  plain third-party repositories.

## 0.4.17 - 2026-05-26

- Treat `scripts/repo_contract_kit.py` as the stable executable entrypoint for
  agent-first kit inspection and planning.
- Add machine-readable version metadata that reports the CLI entrypoint,
  mutating commands, and default non-writing behavior.
- Update tests and maintainer help so agents exercise the executable command
  path directly.

## 0.4.16 - 2026-05-26

- Add `scripts/repo_contract_kit.py` as an AI-first CLI for non-invasive
  orient, status, docs-impact, review-plan, task-packet, and verify commands,
  plus explicit install/update wrappers.
- Document the CLI as the default starting point for external or exploratory
  repo work before installing kit files.
- Add regression coverage for JSON status, docs-impact exit behavior,
  task-packet scaffolding, and explicit install wrapping.

## 0.4.15 - 2026-05-26

- Make `lint_agent_docs.py` resolve literal repo-relative Makefile includes so
  installed targets in `.doc-contract-kit/make/repo-contract.mk` are not
  false-flagged as stale commands.
- Add regression coverage for target-owned root Makefiles that expose kit
  commands through the managed Makefile bridge.

## 0.4.14 - 2026-05-25

- Add installed `make agent-task-cleanup` for auditing task-worktree layouts,
  detecting nested task pools, and moving nested worktrees into the primary
  checkout's flat pool only with explicit apply flags.
- Install the cleanup script and refresh operator docs, harness docs, and
  Makefile help so cleanup is discoverable before manual folder deletion.
- Add regression coverage for dry-run cleanup and applied nested-worktree moves.

## 0.4.13 - 2026-05-25

- Refuse `agent-task-prepare` from linked/task worktrees so new task worktrees
  stay under one flat primary-checkout pool instead of creating nested
  `*-agent-worktrees` directories.
- Update installed operator guidance to treat the primary checkout as the
  coordination point and task worktrees as edit-only execution checkouts.
- Add regression coverage for rejecting nested task preparation.

## 0.4.12 - 2026-05-21

- Add installed `docs/harness-engineering.md` so target repos can see the local
  agent harness components behind startup packets, permissions, research,
  task packets, worktrees, receipts, docs gates, and kit provenance.
- Link the harness view from install-layer docs and installed workflow
  templates so operators can distinguish ownership routing from behavior and
  evidence verification.
- Update installer coverage so new agentic installs include the harness map.

## 0.4.11 - 2026-05-20

- Move installed make targets into the managed
  `.doc-contract-kit/make/repo-contract.mk` fragment so target repos own their
  root `Makefile`.
- Add `make kit-explain` and `kit_status.py --explain` to show the
  installed-kit vs target-repo ownership boundary and existing-repo update
  steps.
- Migrate clean old kit-managed root Makefiles to the new bridge during update
  while preserving customized Makefiles with proposed replacements under
  `.doc-contract-kit/updates/`.

## 0.4.10 - 2026-05-19

- Add installed `make agent-task-status` for checking active task metadata
  against registered git worktrees before launching or handing off parallel
  write-capable agents.
- Report missing, stale, untracked, unknown-scope, and overlapping task
  coordination hazards, with JSON output and strict-mode failure for local
  gating.
- Update installed workflow docs and install tests so target repos expose the
  parallel task status/check surface.

## 0.4.9 - 2026-05-19

- Add `docs/agent-workflow-stack.md` as the install-layer map for deciding
  whether a change belongs in `agent-workflow-kit`, `repo-contract-kit`, or an
  installed target repo.
- Refresh the installed `docs/working-rhythm.md` template so target repos can
  understand source kit vs install kit vs target-repo ownership without reading
  both source repos first.
- Link the stack map from README, repo-boundary guidance, and maintainer help.

## 0.4.8 - 2026-05-19

- Add installed `make kit-refresh KIT=/path/to/repo-contract-kit` to
  fast-forward pull a clean local kit checkout before running the safe managed
  update.
- Update installed workflow docs, rollout guidance, ADR coverage, and startup
  packet update guidance for the refresh command.
- Add regression coverage for clean and dirty `kit-refresh` paths.

## 0.4.7 - 2026-05-19

- Make research runner commands fail before writing artifacts when the
  `review-prompts` research prompt files are not installed.
- Reject unknown research source names instead of producing schema-invalid
  research briefs.
- Add regression coverage for minimal installs and invalid research sources.

## 0.4.6 - 2026-05-19

- Install targeted research prompts, schemas, and local `make
  agent-research-*` commands so target repos can create read-only research
  briefs, source-agent prompts, synthesis artifacts, and task-packet handoffs.
- Add `scripts/agent_research.py` for manual-mode research runs under
  `.agent-workflows/runs/` without mutating backlog, docs, ADRs, issues, or
  source files.
- Add bounded source-plan fields to generated research briefs so source agents
  start from seed URLs, exact queries, allowed domains, artifact budgets, and
  quality floors instead of open-ended search.
- Refresh the vendored `agent-workflow-kit` prompt snapshot with the research
  workflow module.

## 0.4.5 - 2026-05-19

- Install `docs/working-rhythm.md` so target repos have a single human-facing
  guide for the orient, review, scope, and execute flow.
- Add `make workflow-help` / `make help` to installed target repos, plus a root
  maintainer Makefile for this kit.
- Update installer next-step output so new installs start from the working
  rhythm instead of an undifferentiated command list.

## 0.4.4 - 2026-05-14

- Add `make agent-task-prepare TASK=<id>` for approved write-capable tasks. The
  command creates a task branch and sibling worktree, writes local task packet
  and receipt artifacts, records in-flight metadata, and warns or blocks on
  overlapping declared scopes.
- Install ignored `.agent-workflows/tasks/` metadata storage and document the
  worktree-per-task flow in target repo guidance.

## 0.4.3 - 2026-05-14

- Add installed instruction-budget config and linter checks so `AGENTS.md`,
  `REVIEW.md`, and runtime-specific agent rules can stay concise as features
  are added.
- Add agent-instruction hygiene guidance that routes durable rules into scoped
  contracts, checkers, runbooks, ADRs, or receipts instead of stuffing them into
  root instruction files.

## 0.4.2 - 2026-05-14

- Add review-risk and trust-profile context to `make agent-start` packets and
  receipt templates.
- Install an agent tool/network allowlist doc and updated read-only review
  guidance for target repos.
- Refresh the vendored `agent-workflow-kit` prompt/schema snapshot with
  review-risk and local/private/browser policy prompts.

## 0.4.1 - 2026-05-14

- Add script-flow and function-guide comments across the repo-contract-kit
  scripts so maintainers can trace each command's execution path and helper
  roles.

## 0.4.0 - 2026-05-14

- Add agent permission policy templates for read-only review, untrusted PRs,
  browser research, and scoped write-worker profiles.
- Add a fork-safe read-only agent review workflow template and wire installed
  review runs to explicit trust profiles.
- Add strict local session receipt verification with `make agent-receipt-verify`.
- Record vendored `agent-workflow-kit` prompt snapshot provenance in install
  receipts and managed manifests.
- Refresh the vendored prompt/schema snapshot to `agent-workflow-kit`
  `0.2.0-beta.3`, generated from `workflows/prompts`.
- Expand agent instruction linting for secrets, unsafe commands, wildcard
  permissions, browser/account mutation guidance, contradictions, and JSON/SARIF
  output.
- Add repo-boundary documentation for coordinated `agent-workflow-kit` and
  `repo-contract-kit` changes.

## 0.3.0 - 2026-04-30

- Add local agent startup packets.
- Add managed install manifests and safe local update planning.
- Add default target-repo versioning support for agentic installs.

## 0.2.0

- Add local-first agentic profiles, review prompts, TDD prompts, and evidence
  receipt templates.

## 0.1.0

- Bootstrap documentation-contract installer, templates, and local checks.
