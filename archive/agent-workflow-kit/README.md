# agent-workflow-kit

> Status: legacy source checkout. As of 2026-06-18, the canonical workflow
> prompt and schema source has been imported into
> `repo-contract-kit/workflows/`. Use the global `repo-contract-kit` installer
> and CLI for normal setup and management. Use this checkout only for history,
> migration diffs, backlog closeout, and archival validation until it is
> retired. Do not start normal workflow-source or install-layer work here.

Portable local workflows for agentic software development: codebase review,
learning-oriented code comments, TDD/executable specs, remediation planning,
and evidence-backed verification.

The historical prompt source in this checkout lives under `workflows/prompts/`.
`.codex/prompts/` is the generated Codex adapter, and
`.github/copilot-instructions.md` is the generated GitHub Copilot instructions
adapter. The content remains intentionally tool agnostic: AmpCode, Codex,
Claude Code, Aider, Cline, or a human reviewer can use the same Markdown and
JSON schemas directly from the checkout.
For Codex runtimes that consume skills, `make skill-pack-export` also generates
a repo-local skill-pack projection under `dist/codex-skill-pack/` by default.
For review-only local or self-hosted model passes, start from
[`docs/runtime-compatibility.md`](docs/runtime-compatibility.md) and
[`workflows/prompts/policies/local-private-review.md`](workflows/prompts/policies/local-private-review.md)
so the receipt records the actual data boundary, capability caveats, and
escalation decision.

## Where This Fits

Normal target-repo setup should start with the global `repo-contract-kit` CLI,
not with this checkout:

```bash
curl -fsSL https://raw.githubusercontent.com/BoweyLou/repo-contract-kit/main/install.sh | sh
kit setup --preset lite
kit status --json
kit mode-check --json
kit task-packet --harness-mode auto --json
kit verify --harness-mode auto --json
kit update --dry-run --json
```

`kit setup` is a two-word command. Do not use `kit-setup`; the installer writes
one launcher named `kit`, and `setup` is a subcommand of that launcher.

This repository was the workflow-source layer before consolidation:

- focused reviewer personas
- orchestration prompts
- learning-comment workflows
- TDD and executable-spec prompts
- targeted research workflows for backlog, review, design, and architecture
  discovery
- evidence receipt schemas
- task packets that turn backlog items into executable agent work
- deterministic review-risk routing and read-only/private/browser research
  policies
- research and backlog for agentic development workflow quality
- local SemVer versioning with a commit-time gate for version-impacting changes

The public install and management surface is
[repo-contract-kit](https://github.com/BoweyLou/repo-contract-kit). That repo
installs local guardrails into target repositories: `AGENTS.md`, `REVIEW.md`,
docs-impact checks, instruction linting, Make targets, workflow profiles, and
optional adapters.
Target repos should not clone this repo at runtime. `AGW-100` tracks the
consolidation decision that folded the workflow source under
`repo-contract-kit/workflows/`.

When `repo-contract-kit --preset agentic` is installed into a target repo, it
copies a generated workflow snapshot into that repo. New shared prompt-library
work should happen in `repo-contract-kit/workflows/`; use this repo only to
compare or recover historical source material during the archive window.

Installed target repos can generate a concrete review run with
`make agent-run-review AGENT=manual`, or execute the read-only review through
Amp with `make agent-run-review AGENT=amp`.

## Start Here

- [Agent Workflow Stack](docs/agent-workflow-stack.md)
- [Harness Engineering](docs/harness-engineering.md)
- [Codex Review Trace](docs/codex-review-trace.md)
- [Working Rhythm](docs/working-rhythm.md)
- [Maintainer Queue](workflows/prompts/maintainer-queue.md)
- [Multi-Agent Repo Review](workflows/prompts/multi-agent-repo-review.md)
- [Review Map Template](workflows/prompts/templates/review-map.md)
- [Codebase Learning Comments](workflows/prompts/codebase-learning-comments.md)
- [TDD and Executable Specs](workflows/prompts/tdd/README.md)
- [Targeted Research Workflows](workflows/prompts/research/README.md)
- [Task Packet Prompt](workflows/prompts/task-packet.md)
- [Task Worktree Cleanup Prompt](workflows/prompts/task-worktree-cleanup.md)
- [Prompt Index](workflows/prompts/README.md)
- [Usage Recipes](docs/using-the-prompt-kit.md)
- [Local Tool-Agnostic Plan](docs/local-tool-agnostic-plan.md)
- [Runtime Adapters](docs/runtime-adapters.md)
- [Runtime Compatibility](docs/runtime-compatibility.md)
- [Versioning](docs/versioning.md)

## Operating Modes

- `bootstrap`: first pass over a new or inherited repository.
- `drift`: repeated review for docs/code deltas, advisory comment/docstring
  drift, AI slop, duplication, dead code, missed reuse, and operational risk.
- `pull-request`: changed-file review that expands only when the diff crosses a
  shared contract.
- `release-gate`: broad review that can produce blockers and deferred cleanup.
- `learning-comments`: docs/ADR/code/comment pass that adds behavior-neutral
  explanatory comments, or a separate non-developer explanation note when useful
  context should not become source comments. Strict receipts record
  comment-only verification under `evidence.comment_only_verification`; the
  prompt consumes latest-ADR/context evidence first and uses explicit no-ADR
  fallback evidence rather than invented design intent when decision records are
  absent.
- `test-first`: executable-spec pass for TDD, regression tests,
  characterization tests, contract tests, property/invariant tests, and
  test-quality review.
- `research`: source-specific discovery pass for filling backlog, review,
  architecture, design, ADR, risk, or task-packet candidates from auditable
  evidence.

## Repository Layout

- `workflows/manifest.json`: legacy workflow manifest, generated adapter
  list, Codex skill-pack export list, and install-layer boundary.
- `workflows/prompts/`: legacy reusable orchestration, remediation,
  verification, learning, persona, TDD, and template prompts.
- `.codex/prompts/`: generated Codex projection of `workflows/prompts/`.
- `.github/copilot-instructions.md`: generated GitHub Copilot projection of
  the workflow source.
- `schemas/`: local JSON schemas for receipts, task packets, persona
  manifests, review synthesis artifacts, review maps, regression fixtures, and
  agent permission policies.
- `scripts/`: stdlib validation and regression-fixture harnesses for local
  workflow guardrails, docs-impact benchmarks, plus local versioning checks.
- `docs/`: usage recipes and local-first workflow notes.
- `research/`: feature matrix, source findings, regression fixtures,
  docs-impact benchmark fixtures, and backlog for the broader agentic
  development workflow. The aggregate
  ecosystem backlog is split into repo-owned views so implementation work checks
  both this repo and `repo-contract-kit` before changing either side.

## Local Checks

```bash
make workflow-help
make validate
make self-check
make docs-check
make agent-start
make kit-status
make agent-next
make backlog-status
make backlog-check
make agent-verify
make docs-freshness
make agent-token-budget
make prompt-adapters-check
make skill-pack-export
make skill-pack-check
make backlog-split-check
make version-check
make context-packet
python3 scripts/classify_review_risk.py --working-tree
python3 scripts/run_docs_impact_benchmarks.py
python3 scripts/run_prompt_regression_fixtures.py
```

This repo dogfoods `repo-contract-kit --preset agentic`. Use `AGENTS.md`,
`REVIEW.md`, `.agent-workflows/`, `doc-contract.json`, and the `make agent-*`
targets as the local guardrail surface for review, docs impact, instruction
hygiene, task packets, and evidence receipts.

Run `make self-check` when using the guardrails to organize this repo. It keeps
the source-repo boundary explicit: live workflow source belongs in
`repo-contract-kit/workflows/`, local `workflows/prompts/` is legacy/archive
material, `.codex/prompts/` is its generated mirror, and `kit-update` /
`kit-refresh` stay opt-in maintenance commands.

Use `make kit-refresh KIT=/path/to/repo-contract-kit` when the local
`repo-contract-kit` checkout should be pulled fast-forward first, then applied
through the safe managed-file updater. Use `make kit-update
KIT=/path/to/repo-contract-kit` directly when intentionally installing from an
unpushed local kit checkout.

Run `make prompt-adapters-export` after archive-maintenance edits under
`workflows/prompts/` or `workflows/manifest.json`. `make validate` fails when
generated adapters are not in sync with the legacy prompt tree. Current prompt,
schema, adapter, and task-packet source edits should happen in
`repo-contract-kit/workflows/`.

Run `make skill-pack-export` to materialize Codex skill folders from selected
workflow prompts. The default output is `dist/codex-skill-pack/`, which is
repo-local and ignored by Git. Use `SKILL_PACK_OUTPUT=/path/to/pack` to choose
another artifact directory and `SKILL_PACK_SKILLS="review task-packet"` to
export a subset. `make skill-pack-check` verifies that an existing pack matches
the deterministic export.

Run `make backlog-split` after editing
`research/agentic-workflow-review/backlog.csv`. `make validate` fails when the
repo-owned split files are not in sync.

Run `make install-git-hooks` once per checkout to make Git run the local
versioning gate before every commit. The hook requires `VERSION` and
`CHANGELOG.md` to be staged when prompts, schemas, scripts, examples, or repo
governance files change.

Use `make version-bump BUMP=patch|minor|major` before committing
version-impacting work, then replace the generated changelog stub with a
specific note.

Use `make context-packet` before broad review work to generate a deterministic
changed-file packet with likely callers, tests, docs, ADRs, scripts, and runtime
configuration. For large changesets, fill
`workflows/prompts/templates/review-map.md` and validate structured maps against
`schemas/review-map.schema.json` so reviewers get changed-file clusters,
entrypoints, contracts, risk hotspots, review sequence, validation evidence,
omissions, and follow-up packet candidates. Review maps organize evidence from
context packets or installed context bundles; they do not replace direct source,
tests, docs, ADRs, scripts, runtime-config, or receipt inspection. Use
`make receipt-summary RECEIPT=/path/to/receipt.json` to render a concise
Markdown handoff from a completed session receipt.
Session receipts can include optional `harness_metrics.review_outcome` and
`harness_metrics.effort` groups for review yield, false-positive and duplicate
rates, latency, time to green, cost/token effort, and human review burden.
Treat these as calibration evidence, not productivity proof: read them beside
finding severity, false-positive notes, duplicate rate, human decisions, review
time, and validation quality, and omit unknown cost, latency, or human-burden
values instead of guessing.
Use [Codex Review Trace](docs/codex-review-trace.md) for the source-side
`codex-review trace` concept when a future local interface needs to open,
export, or debug run evidence. That page is CLI-later guidance only; this repo
does not ship a `codex-review trace` command or Make target today.

Use `make agent-next` when returning to the workflow stack. It combines backlog
source state, dirty working tree state, and active task metadata so the next
safe handoff is visible without manually reconciling several files.

Use `make docs-freshness` for executable documentation truth checks beyond
path-based docs impact: local Markdown links, documented Make targets, script
references, and schema references. Use `make agent-token-budget` to report the
token footprint of agent-facing context files before prompt or instruction
growth becomes invisible.

Use `python3 scripts/run_prompt_regression_fixtures.py` to check deterministic
persona and synthesis output examples for required finding fields, concrete
evidence, false-positive notes, advisory comment/docstring drift labels, nit
suppression, source-persona preservation, and duplicate synthesis discipline.

Use the working rhythm as the default human-facing path: orient with
`make agent-start` and `make kit-status`, review with `make agent-run-review`,
scope with `make agent-task-packet`, then execute approved write work through
the installed target repo's `make agent-task-status` and
`make agent-task-prepare`. Long-running task workers can refresh leases with
`make agent-task-heartbeat TASK=<id>` and close metadata plus evidence with the
installed lifecycle commands: `make agent-task-finish`,
`make agent-task-block`, or `make agent-task-abandon`. Where the installed kit
exposes the task finalizer, use it to combine readiness, lifecycle, final
status, and closeout-preview evidence before handoff.

Use `python3 scripts/classify_review_risk.py --working-tree` before dispatching
reviewers. It emits a risk tier, trust profile, trigger list, and recommended
personas so high-risk auth, data, API, CI, runtime, and frontend changes get
specialist review while normal changes stay narrow.

## Review Flow

1. Run the orchestrator prompt to map the repository and dispatch persona
   reviewers.
2. Give each reviewer one focused prompt from `workflows/prompts/personas/`.
3. Merge their findings with `workflows/prompts/review-synthesis.md`.
4. Convert accepted findings into scoped remediation with
   `workflows/prompts/fix-planner.md`.
5. Run implementation and verification prompts only after the review findings
   are evidence-backed.

Machine-readable synthesis should validate against
`schemas/review-synthesis.schema.json` before a runner or follow-on agent treats
findings as executable work.

## Maintainer Queue Flow

Use `workflows/prompts/maintainer-queue.md` when you need a compact view of
active work, owner decisions, next packet candidates, and blockers. It reads the
same local signals as the rest of the harness: `make backlog-status`,
`make agent-next`, `make agent-task-status`, task packets, receipts, and
readiness reports. Queue analysis stays read-only unless a separate task packet
or explicit owner instruction grants more authority.

## Backlog Flow

Use `workflows/prompts/task-packet.md` when a backlog item, issue, accepted
finding, or broad request needs to become executable work. The packet captures
scope, acceptance criteria, validation, closeout requirements, docs impact,
risk, and approval state so the backlog remains planning input rather than a
separate product surface.
Installed targets can surface portable backlog state with `make backlog-status`
and `make backlog-check`, then generate a starter packet with
`make agent-task-packet-from-backlog BACKLOG_ID=<id>`.

## Research Flow

Use `workflows/prompts/research/` when a repo or product question needs targeted
source collection before implementation. Start with a research brief, dispatch
one source agent per source family, then synthesize source reports into proposed
backlog rows, review questions, architecture/design notes, ADR candidates, risk
items, or task-packet candidates. Research agents stay read-only and produce
proposals until a human approves a write step.

## Learning Flow

Use `workflows/prompts/codebase-learning-comments.md` when the goal is
understanding rather than defect review. It compares docs, latest ADRs,
existing comments, and actual code before proposing comment-only edits that
explain intent, invariants, domain terms, and non-obvious flow. For
non-developer explainability, it can instead produce a plain-language note that
maps domain terms, data flow, external boundaries, state transitions,
operational constraints, and surprising guardrails without assuming the reader
will edit code. It starts from existing agent-start latest-ADR evidence,
context-packet or context-bundle ADR items, and task/operator decision
references before manual ADR scanning; when no ADR or decision record exists,
it records that absence and uses README, docs, tests, code, config, changelog,
task context, and operator instructions as fallback evidence. The run receipt
should include
`evidence.comment_only_verification` with the diff scope, no-behavior assertion,
reviewed paths, evidence commands, explanation-note path explanations, and any
uncertainty so strict validation can prove the run stayed behavior-neutral.

## Test-First Flow

Use `workflows/prompts/tdd/` when accepted review findings or new features should
be implemented through executable behavior. The set covers test-first feature
work, regression-first bug fixes, characterization before refactor, outside-in
acceptance TDD, property/invariant tests, contract tests, refactoring under
tests, test-quality review, and an optional TCR micro-loop.

## Public Repository

This repo is published as
[BoweyLou/agent-workflow-kit](https://github.com/BoweyLou/agent-workflow-kit).
