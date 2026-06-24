# kit

`kit` is the single repository and public command for the installable repository
contract kit. It adds documentation contracts, agent instruction hygiene,
evidence receipts, local verification commands, and optional workflow profiles
to target repositories.

Documentation freshness is still the core contract. The scope has grown because
agent-heavy repositories also need explicit local rules for prompts, reviewers,
tests, receipts, and tool-agnostic workflows.

## What this repo contains

- templates for repo-local operating guardrails
- a lightweight documentation impact checker
- a simple installer for bootstrapping target repositories
- an AI-first CLI for non-invasive status, docs-impact, planning, and explicit
  install/update operations
- local-first agent workflow files that work without GitHub Actions or hosted CI
- agent instruction linting for local prompt/rule files
- no-write instruction diet audits that propose where bulky agent-facing detail
  should move before humans prune it
- branch-or-PR readiness aggregation across local git, docs, changelog, task,
  receipt, review-disposition, and explicit CI/check evidence
- docs patch proposal artifacts that stay outside the target checkout until
  reviewed
- an experimental docs-as-tests profile for declared local API documentation
  assertions
- instruction budgets so `AGENTS.md` and tool-specific rule files stay concise
- explicit permission policies for read-only review, untrusted PRs, browser
  research, and scoped write workers
- review-risk and trust-profile startup context
- targeted research commands for source-specific backlog, review, design, and
  architecture discovery
- backlog source discovery, backlog checks, next-task recommendation, and
  backlog-row-to-task-packet handoff
- deterministic lite, standard, and release-gated harness mode selection for
  matching task-packet weight to local risk
- planning adapter examples for Keryx, Obsidian, issues, and repo backlog
  mirrors without external writes
- evidence receipt and safe-output schemas
- TDD/executable-spec workflow profiles
- safe local kit updates with managed-file conflict reports
- optional managed runtime instruction adapters for Claude Code and GitHub
  Copilot
- an explicit opt-in private-context profile with ignored local context
  templates and privacy warnings
- workflow prompt snapshot provenance for generated agent files
- default local SemVer files and version commands for agentic target repos
- beginner-friendly docs explaining PRs, CI, hooks, ADRs, and agent instructions
- a Hermes skill stub for later automation

## Where This Fits

This repository is the install layer:

- `AGENTS.md` and `REVIEW.md` templates
- docs-impact checks and waivers
- local `make` targets
- profile installation, managed manifests, and update receipts
- local agent workflow files under `.agent-workflows/`
- optional thin runtime adapters such as `CLAUDE.md` and
  `.github/copilot-instructions.md`
- tool-agnostic schemas and safe-output boundaries
- installed provenance for `repo-contract-kit` and the computed
  `workflow-source` prompt snapshot
- optional fork-safe read-only PR workflow adapter

The workflow source now lives in this repo under `workflows/`. That directory
owns the prompt library, reviewer personas, learning-comments workflows, TDD
prompts, synthesis prompts, and research prompt source. Target-repo operators do
not need a second checkout.

For the cross-repo ownership map, read
[`docs/agent-workflow-stack.md`](docs/agent-workflow-stack.md). It explains
where to edit prompt/source changes, installer changes, target-repo operator
guidance, and release pairing.
For the version 1 repository identity, archive policy, compatibility gate, and
rollback path, read
[`docs/version-1-consolidation.md`](docs/version-1-consolidation.md).
For the installed harness view, read
[`docs/harness-engineering.md`](docs/harness-engineering.md). It maps the local
commands, policies, receipts, task worktrees, docs gates, and update metadata to
the agent behavior each surface shapes.

## Core idea

A code change is not complete until the repository has either:

1. updated the relevant documentation, or
2. explicitly declared why no documentation update is needed

## Current Scope

This project aims to be:

- simple
- understandable
- easy to install locally
- easy to iterate on
- useful without hosted CI or a specific coding agent

It does not yet try to solve every language, build system, or CI pattern.

## Quick start

The preferred two-surface setup is:

1. Install the global launcher once per machine.
2. From each repository, enroll that repo as a target.

Download and run the installer:

```bash
curl -fsSL https://raw.githubusercontent.com/BoweyLou/kit/main/install.sh | sh
```

The installer caches a `kit` checkout outside target repositories and
writes a `kit` launcher to `~/.local/bin` by default. Target repos do not
receive or use a workflow-source checkout at runtime. Add `~/.local/bin` to
`PATH` if your shell does not already include it.

If another tool already owns `kit`, the installer refuses to overwrite it. Pick
a different launcher with `--command-name NAME` or `KIT_COMMAND=NAME`. The old
`REPO_CONTRACT_KIT_COMMAND` environment variable still works as a temporary
compatibility fallback.

Default global source path:

```text
~/.local/share/kit/source
```

Maintainers who still need the legacy external workflow-source checkout for
migration can opt in:

```bash
sh /tmp/kit-install.sh --with-workflow
```

That compatibility path adds:

```text
~/.local/share/agent-workflow-kit/source
```

Then, inside each target repository:

```bash
kit setup
```

`kit setup` is a two-word command. Do not use `kit-setup`; the installer writes
one launcher named `kit`, and `setup` is a subcommand of that launcher.
Agents should resolve the launcher with `command -v kit` and then run this
subcommand from the target repo; they should not search the workspace for a
separate setup script.

Use `--repo /path/to/repo` when enrolling a repo from another directory:

```bash
kit setup --repo /path/to/target/repo --preset agentic
```

### Updating global and target installs

The global launcher points at a cached `repo-contract-kit` checkout. Updating the
global tool updates that cache. If the optional maintainer workflow-source
checkout was installed, it updates that checkout too. It does not rewrite any
target repository by itself.

Check and update the global tool:

```bash
kit
kit update --global
kit options
```

Then update each enrolled target repo when you want that repo to receive the
new managed files and prompt snapshot:

```bash
kit status --json
kit mode-check --json
kit task-packet --harness-mode auto --json
kit verify --harness-mode auto --json
kit update --dry-run --json
```

Use `docs/upgrade-flow.md` for the full target-repo sequence: inspect status,
preview the update, review conflict proposals, run metadata-only migration when
needed, apply the managed update, diagnose, and verify. The flow does not move
or remove root `AGENTS.md`; customized managed files are preserved with proposed
replacements under `.doc-contract-kit/updates/`.

For a local batch across many repos, keep the target update explicit:

```bash
for repo in /path/to/repo-a /path/to/repo-b /path/to/repo-c; do
  (cd "$repo" && kit update)
done
```

`kit update` uses the same safe managed updater as `make kit-update`: it
preserves target-owned files, preserves customized managed files with conflict
reports under `.doc-contract-kit/updates/`, and records the installed
`repo-contract-kit` plus computed `workflow-source` prompt snapshot provenance
in the target repo metadata. `kit update --json` has the same apply-by-default
semantics and returns machine-readable write paths; use
`kit update --dry-run --json` or `kit update-plan --json` for a non-mutating
plan. Human `kit update --dry-run` and `kit update` output starts with a
compact summary of blockers, conflicts, direct updates, target-owned files,
proposal paths, target and sidecar writes, and next commands. Add `--verbose`
when you need the raw updater detail after that summary.
For human summaries, `--style auto|plain|pretty` controls restrained ANSI
emphasis. `auto` uses ANSI only on a TTY, `plain` forces script-friendly text,
and `pretty` forces emphasis unless `NO_COLOR` is set. JSON output never uses
ANSI styling, and no output depends on color for meaning.

The target repo never clones a workflow-source repo. Target repos receive the
prompt snapshot generated from `kit/workflows/` and recorded in
`repo-contract-kit`; maintainers refresh that generated snapshot intentionally
inside this repo.

If a target repo accidentally has a nested source checkout, preview and repair
it before enrolling or updating:

```bash
kit target repair-source-clone
kit target repair-source-clone --apply
kit setup
```

The repair command only removes detected nested `repo-contract-kit` or legacy
workflow-source directories. It refuses to delete the repository root, blocks
when unrelated target files are dirty, and reports next target-mode commands in
JSON for automation.

For an AI agent or local maintainer that should inspect a repo without writing
kit files into it, start with the CLI:

```bash
kit version --json
kit command-map --json
kit agent-context --json
kit agent-tool-manifest --json
kit self status --json
kit orient --repo /path/to/repo --json
kit sidecar-init --repo /path/to/repo --json
kit agent-self-heal --repo /path/to/repo --json
kit backlog-status --repo /path/to/repo --json
kit agent-next --repo /path/to/repo --json
kit instruction-diet --repo /path/to/repo --json
kit agent-state-ledger --repo /path/to/repo --json
kit feedback --repo /path/to/repo --export-json
kit branch-readiness --repo /path/to/repo --json
kit doc-impact --repo /path/to/repo --working-tree --json
kit review-plan --repo /path/to/repo --mode pull-request --json
kit onboarding-pr --repo /path/to/repo --preset agentic --json
kit verify --repo /path/to/repo --json
kit update-plan --repo /path/to/repo --json
kit status --repo /path/to/repo --json
```

These commands are non-interactive and machine-readable when `--json` is set.
They do not install `AGENTS.md`, `.agent-workflows/`, `.doc-contract-kit/`, or
other kit files into the target repo. Their JSON includes
no-write metadata plus deterministic sidecar state paths under
`${XDG_STATE_HOME:-~/.local/state}/repo-contract-kit/` so agents know where
startup packets, receipts, review artifacts, task packets, and onboarding
bundles would live without polluting a third-party checkout. Most commands use
`target_repo_writes.performed: false`; `agent-state-ledger` also returns the
top-level booleans `target_repo_writes=false` and `sidecar_writes=false` for
startup-safe gating. The read-only commands only report those paths; they do
not create the sidecar directories.
Use `command-map --json` to discover command paths, flags, JSON support,
mutation classes, sidecar write behavior, aliases, examples, output schema
pointers, docs pointers, and route taxonomy from the CLI itself. Each command
declares a `route_role` such as `canonical`, `alias`, `agent-only`,
`compatibility`, `maintainer`, or `namespace`, plus `canonical_command`,
`alias_group`, and `route_note` fields where the relationship is ambiguous. For
example,
`kit setup` is the canonical target-enrollment route, `kit target add` is its
explicit namespace alias, and `kit install` remains the explicit agent/source
install route. `agent-context --json` returns the same catalogue under an
agent-oriented alias.

### Agent tool manifest

Use `agent-tool-manifest --json` when a local agent, MCP adapter, or other
automation layer needs a compact command contract instead of the full command
catalogue. The manifest is derived from `command-map --json` and separates
read-only safe commands, target-writing commands, sidecar-writing commands,
output schemas, examples, and non-interactive behavior.

The manifest is local-only metadata. It does not call a hosted model, use
credentials, reach the network, write target repo files, or write sidecar state.
Agents should treat `--no-input` or `KIT_AGENT=1` as the non-interactive
contract, prefer JSON mode, and ignore unknown additive fields in future schema
versions.

### JSON payload contracts

JSON responses are schema-versioned with a top-level `schema_version` field.
Within a schema version, existing stable fields keep their meaning; future kit
versions may add fields. Agent callers should ignore unknown fields and use
`command-map --json` to discover the current command surface before selecting a
route.

Each command-map entry includes a `json_contract` block that states whether the
command supports JSON, its `output_schema` name, the stable payload fields to
expect, the command-map fields that describe write behavior, and a
`schema_pointer` back to this section. Commands such as `help`, `options`,
`self`, and `target` intentionally do not expose direct JSON payloads; their
contracts say whether to use `command-map --json` or inspect subcommands.

Agent-facing JSON payloads include `schema_version` and `command`. JSON commands
that can be used for startup or automation also expose write metadata through
`target_repo_writes` and `sidecar_writes`; `version --json` reports those fields
as read-only no-write metadata. Commands that use legacy top-level booleans,
such as `agent-state-ledger` and `branch-readiness`, keep those fields for
compatibility while also documenting the no-write guarantee in their payload.

### Shell completions

`kit completion bash|zsh|fish` prints shell completion code to stdout. The
completion scripts are generated from the parser-backed command map and include
command paths, nested subcommands, and parser flags. The command does not write
shell configuration files; install it explicitly with a redirect or command
substitution.

Bash:

```bash
mkdir -p ~/.local/share/bash-completion/completions
kit completion bash > ~/.local/share/bash-completion/completions/kit
```

Zsh:

```bash
mkdir -p ~/.zsh/completions
kit completion zsh > ~/.zsh/completions/_kit
fpath=(~/.zsh/completions $fpath)
autoload -Uz compinit && compinit
```

Fish:

```bash
mkdir -p ~/.config/fish/completions
kit completion fish > ~/.config/fish/completions/kit.fish
```

### TTY command palette

`kit palette` opens a dependency-free command search surface for interactive
TTY sessions. It searches command names, summaries, examples, and mutation
classes from the same parser-backed command map used by `command-map --json`
and shell completions. Use `--query` to start with a search term and
`--print-command` to print the first exact command preview without entering the
chooser.

```bash
kit palette
kit palette --query status
kit palette --query status --print-command
```

The palette never runs the selected command. It prints the exact shell command,
mutation class, target-write behavior, and sidecar-write behavior. Mutating
commands require an explicit `yes` confirmation before the exact command is
printed. The palette is disabled in non-TTY sessions, under `--no-input`, and
under `KIT_AGENT=1`; use `kit command-map --json`, `kit options`, or shell
completion output for non-interactive discovery.

Parse errors are concise in text mode and include did-you-mean suggestions
without dumping full global help. When `--json` is present anywhere in the
attempted argv, or `KIT_AGENT=1` is set, parse failures return a
schema-versioned JSON envelope with `command: "parse-error"`, error kind,
offending token, suggestions, next commands, and no-write metadata.
Use the global `--no-input` flag for scripted runs that should never prompt.
`KIT_AGENT=1` implies non-interactive mode and also requests JSON parse-error
recovery. JSON payloads expose `non_interactive`, `agent_mode`, and an
`input_contract` block so callers can gate prompt-sensitive flows. In text mode,
help/status/parse-error output goes to the normal human channel and exits
without prompting when `--no-input` or `KIT_AGENT=1` is active.
Human help is grouped by daily, agent/automation, and maintainer lanes.
`kit --help` and `kit options` show common scenarios first, while
`kit help --all` keeps the full advanced command inventory discoverable.
Text `kit status` labels the running tool version, target install version,
target repo version, prompt snapshot, and source refs separately before
suggesting the next setup or update-preview command.
Use `agent-self-heal` to preview sidecar initialization and stale generated
task-state quarantine without writing by default. Apply mode requires
`--apply`, refuses unrelated tracked source changes, reports unrecognized
untracked files without deleting them, and writes a sidecar before/after
receipt. It is not a source cleanup, stash, reset, or task-worktree removal
command.
Use `sidecar-init` or `--write-sidecar` on `orient`, `review-plan`,
`docs-propose`, `onboarding-pr`, `task-packet`, or `verify` when an agent should
write run artifacts outside the target repo while still reporting
`target_repo_writes.performed: false`.
Use `kit feedback --repo /path/to/repo --message "..."`
to append local CLI friction notes to the repo sidecar JSONL ledger. Use
`kit feedback --repo /path/to/repo --export-json` to inspect the ledger without
creating sidecar state. Feedback stays local by default: the command performs no
network calls, creates no issue, submits nothing upstream, and never writes into
the target repo.
Use the explicit `install` or `update` subcommands only when repo-owner adoption
or maintenance is intended.
The stable agent-facing entrypoint is the global `kit` launcher when installed.
The checkout-local executable `scripts/repo_contract_kit.py`
remains the portable fallback for development or filesystems that do not
preserve executable mode.

From inside this repo:

```bash
kit setup --repo /path/to/target/repo
```

For small repos and low-risk local tasks, install the lite preset:

```bash
kit setup --repo /path/to/target/repo --preset lite
```

The `lite` preset installs the minimal documentation contract plus
`docs/lite-mode.md` and `docs/sidecar-retention.md`. It does not install prompt
packs, runtime-specific adapters, or target versioning files.

For the opinionated agentic setup:

```bash
kit setup --repo /path/to/target/repo --preset agentic
```

The `agentic` preset is local-first and agent-tool agnostic. It can be used from
AmpCode, Codex, Claude Code, Aider, Cline, or a manual shell workflow. It does
not require GitHub Actions and is suitable for locked-down on-prem Git servers
such as older Bitbucket deployments.

Runtime-specific instruction files are opt-in so the kit does not create a
second prompt source by default. To add thin managed adapters for Claude Code
and GitHub Copilot:

```bash
kit setup --repo /path/to/target/repo --preset agentic --runtime-adapters claude-code,github-copilot
```

See [`docs/runtime-adapters.md`](docs/runtime-adapters.md) for the supported
adapters and update behavior.

Private context templates are also opt-in. Install them only when the repo owner
wants ignored local files for agent-facing project notes, user preferences, or
private local reminders:

```bash
kit setup --repo /path/to/target/repo --profile private-context
```

The profile creates `.agent-context/` with README and `.example.md` guidance
only. Its managed `.gitignore` tracks the examples and ignores real local
context files by default. Do not put secrets, tokens, cookies, passwords,
private URLs, account identifiers, customer data, personal messages, medical or
financial data, or proprietary snippets that should not leave the machine in
that directory. Review and redact any local context before sharing it with
hosted models, browser tools, GitHub comments, pull requests, issues, external
tickets, or chat tools.

If you are already inside the target repo and this kit is cloned locally:

```bash
python3 /path/to/kit/scripts/install.py "$(pwd)" --preset agentic
```

If you do not have the kit cloned yet and internet access is available:

```bash
tmp="$(mktemp -d)" && git clone --depth 1 https://github.com/BoweyLou/kit "$tmp/repo-contract-kit" && python3 "$tmp/repo-contract-kit/scripts/install.py" "$(pwd)" --preset agentic
```

Then inside the target repo:

```bash
make workflow-help
make agent-start
make goal-check
make kit-status
make agent-next
make agent-context-bundle
make agent-state-ledger
make agent-branch-readiness
make agent-self-heal
make docs-as-tests
make backlog-status
make backlog-check
make kit-explain
make docs-check
make agent-docs-lint
make agent-instruction-diet
make agent-docs-localize
make agent-docs-explain
make agent-docs-propose
make agent-changelog-update
make agent-review
make agent-run-review AGENT=manual
make agent-run-review AGENT=manual AGENT_TRUST_PROFILE=untrusted-pr
make agent-research-plan
make agent-research-run RESEARCH_SOURCE=github
make agent-research-synthesize
make agent-research-to-task-packet
make agent-receipt-verify
make agent-task-packet
make agent-task-packet-from-backlog BACKLOG_ID=<id>
make agent-task-prepare TASK=<id> SCOPE=<paths>
make agent-task-ready
make agent-automation-handoff
make agent-task-heartbeat TASK=<id>
make agent-task-finish TASK=<id> TASK_RECEIPT=<path>
make agent-task-closeout
make agent-token-budget
make agent-test-first
make version-check
```

The everyday rhythm is four moves: orient, review, scope, execute. Use
`make workflow-help` or `docs/working-rhythm.md` in the target repo before
digging into the lower-level command reference.
The research commands require the `review-prompts` profile, which is included
in the `agentic` preset.

## Start an Agent in an Existing Repo

After installing the `agentic` preset, generate a local session packet:

```bash
make agent-start
```

Use `MODE` when you already know the session type:

```bash
make agent-start MODE=drift
make agent-start MODE=test-first
```

The command writes an ignored local packet under `.agent-workflows/runs/` with
an agent brief, machine-readable startup context, and a receipt template. It
records failed discovery checks as warnings instead of blocking startup.
The packet includes a `review_risk` block with the risk tier, selected trust
profile, trigger rules, policy docs, and guidance for whether specialist
reviewers are needed.
It also includes a compact `goal_check` summary from
`.agent-workflows/area-contracts.json`, so changed files are mapped to declared
area contracts before an agent has to reread broad repo docs.

If you want to start manually, point Codex, AmpCode, or another local coding
agent at the target repo and give it this brief:

```text
Read AGENTS.md, REVIEW.md, and .agent-workflows/README.md.
Then follow .agent-workflows/repo-review.md in bootstrap mode.
Use the installed personas and prompts under .codex/prompts/ where useful.
Start by running make agent-verify and make agent-docs-localize.
Produce a findings backlog before editing code.
```

You can also run `make agent-review` in the target repo to print this brief
locally.

To materialize a read-only review run, use:

```bash
make agent-run-review AGENT=manual
```

Manual mode creates prompts and placeholder JSON artifacts under the latest
`.agent-workflows/runs/<id>/review-run/` directory. When Amp is installed and
signed in, use:

```bash
make agent-run-review AGENT=amp
```

The Amp adapter calls `amp --execute --stream-json`, saves raw output, extracts
JSON findings, runs synthesis, and fails the run if git status changes during a
read-only reviewer or synthesis call.

Review runs use `.agent-workflows/agent-permission-policy.json`; the default is
`read-only-review`, and `AGENT_TRUST_PROFILE=untrusted-pr` keeps fork-origin or
otherwise untrusted changes artifact-only with no write-back, PR mutation,
browser account mutation, or secret access.

Validate completed run evidence with:

```bash
make agent-receipt-verify
make agent-receipt-verify RECEIPT=.agent-workflows/runs/<run-id>/review-run/receipt.json
```

Strict receipt validation fails when required local evidence is missing or
malformed.

The installer copies a generated snapshot of the prompt library into the target
repo under `.codex/prompts/`. Improve those prompts in
`kit/workflows/prompts/`, run `make workflow-source-export`, and
ship the updated templates through a normal target update.

## Updating An Installed Repo

Installs write `.doc-contract-kit/install.json` and
`.doc-contract-kit/manifest.json`. The manifest records the managed files,
their source templates, hashes, installed kit version, source ref, and the
workflow prompt snapshot ref/hash. Both files also record
`profile_config_schema_version` so newer kit checkouts can detect when selected
profiles, presets, runtime adapters, or install metadata need a safe metadata
migration.

From the target repo, check what is installed:

```bash
make kit-status
```

Prefer the global CLI for updates:

```bash
kit status
kit update --dry-run
kit update
kit doctor
```

`kit status` prints the installed kit, prompt snapshot, managed-file status,
target repo version, and a `Kit drift` diagnostic that compares the running
global tool against the target install receipt, source ref, and prompt snapshot.
The drift classification is `acceptable`, `stale`, `newer-target`, `unknown`,
or `not-installed`, and status prints safe next commands such as
`kit update --dry-run --repo /path/to/repo` or `kit update --global` without
applying them. `make agent-start` includes the same freshness signal in its
startup packet and keeps the selected policy `report-only`; agents should use
the recommended dry-run or maintenance command before write-capable work when
freshness is stale, newer-target, or unknown. `kit update --dry-run` previews
managed-file writes, profile/config migrations, and conflicts before anything
changes. `kit doctor`
runs non-mutating dirty-state, task, worktree, kit-drift, and recovery-command
diagnostics from the global CLI. The update and doctor commands lead with
compact human summaries; use `kit update --verbose` or
`kit target update --verbose` to include raw updater detail after the summary.
Use `--style pretty` for restrained ANSI emphasis in interactive summaries,
`--style plain` for captures, or `NO_COLOR=1` to suppress ANSI everywhere.

When the global CLI is unavailable, use the local Make fallback:

```bash
make kit-status KIT=/path/to/kit
make kit-update KIT=/path/to/kit
```

To migrate only installed profile/config metadata after `update-plan` reports a
missing or outdated schema marker:

```bash
make kit-migrate-config KIT=/path/to/kit
```

To add or change selected runtime adapters during update:

```bash
kit update --runtime-adapters claude-code,github-copilot
```

The updater is plan-first at the script level and preview-first from the human
CLI when `--dry-run` is passed. Use
`repo_contract_kit.py update-plan --repo /path/to/repo --json` or
`python3 /path/to/kit/scripts/update.py /path/to/repo --plan-json`
to inspect no-install, legacy, current, customized-file, missing-file, Makefile
boundary, invalid-metadata, dirty-repo, and profile/config schema states without
writing files. When profile/config metadata is missing or outdated, the plan
reports `migrate-profile-config` plus an explicit `--metadata-only` command.
Installed `make kit-migrate-config` passes that metadata-only apply path and
updates only `.doc-contract-kit/install.json` and
`.doc-contract-kit/manifest.json`; it does not rewrite target-owned files,
managed files, or customized managed-file conflict baselines. Installed
`make kit-update` passes the full explicit apply flag. It overwrites a
kit-managed file only when the target file still matches the last installed
hash. If the target file was customized, it is preserved and a proposed
replacement plus report is written under `.doc-contract-kit/updates/`.
Plans and reports include a `read_next` list that points the updating agent or
operator at the target repo instructions, workflow docs, and this kit checkout's
`CHANGELOG.md` before accepting proposed replacements.
They also include `after_update` sidecar commands. After updating a repo to a
sidecar-capable kit version, run `sidecar-init` once for that target repo and
tell future agents to pass `--write-sidecar` to `orient`, `review-plan`,
`task-packet`, and `verify` when they should keep generated packets and receipts
outside the target checkout. Existing `.agent-workflows/runs/`,
`.agent-workflows/tasks/`, and `.doc-contract-kit/updates/` artifacts are not
moved automatically; review and archive or move them intentionally.

For maintainers dogfooding the workflow source checkout, there is a deprecated
compatibility shim that can still update both the current target repo and the
local workflow source checkout from one command:

```bash
STACK_UPDATE_COMPAT=1 make kit-update-stack
```

This is not a normal target-repo maintenance path, and ordinary target repos
should use `kit update` instead. The compatibility command
discovers `repo-contract-kit` and the workflow source from
`REPO_CONTRACT_KIT`/`KIT`, `AGENT_WORKFLOW_KIT`/`WORKFLOW`, parent directories,
and common local checkout roots. If discovery cannot find the right checkout,
pass explicit overrides:

```bash
STACK_UPDATE_COMPAT=1 make kit-update-stack KIT=/path/to/kit WORKFLOW=/path/to/Codex_CodeReview
```

The command applies the same safe managed updater to the target repo first and
then to the workflow source repo. It preserves customized managed files in each
repo and writes separate update reports under each repo's
`.doc-contract-kit/updates/` directory.

When the global CLI is unavailable and a local kit checkout should be refreshed
first, use the legacy fallback:

```bash
make kit-refresh KIT=/path/to/kit
```

`kit-refresh` verifies that `KIT` is a clean git checkout, runs
`git pull --ff-only`, prints `kit-status` with the refreshed checkout, and then
runs `kit-update`. If the kit checkout has local changes, commit or stash them
first, or run `kit-update` explicitly when you intentionally want to use that
local working tree.

Use `STACK_UPDATE_COMPAT=1 make kit-refresh-stack` only for maintainer dogfood
work when the first step should be a clean fast-forward pull of the kit checkout
and then the target-plus-workflow update. Pass `KIT=...` or `WORKFLOW=...` only
when discovery needs an override.

For internet-enabled repos that do not keep the kit cloned:

```bash
curl -fsSL -o /tmp/kit-install.sh https://raw.githubusercontent.com/BoweyLou/kit/main/install.sh
sh /tmp/kit-install.sh
kit update --dry-run
kit update
```

If a legacy install has no manifest, the first update run adopts current file
hashes without overwriting. Re-run the update command after adoption to apply
safe updates.

### Makefile boundary for existing installs

The target repo owns its root `Makefile`. New installs write a small bridge only
when no `Makefile` already exists:

```make
include .doc-contract-kit/make/repo-contract.mk
```

The kit-owned make targets live in `.doc-contract-kit/make/repo-contract.mk`.
When an older installed repo updates:

- a clean old kit-managed root `Makefile` is migrated to the small target-owned
  bridge automatically;
- a customized root `Makefile` is preserved, and the updater writes a proposed
  bridge under `.doc-contract-kit/updates/`;
- a target-owned root `Makefile` that already defines kit targets directly is
  reported as direct-local maintenance instead of missing commands;
- `make kit-status` and `make kit-explain` report whether the Makefile bridge
  is present and what to do next.

## Versioning

The kit itself uses root `VERSION` plus `CHANGELOG.md`. Release tags should use
SemVer names such as `v0.3.0` when tags are available, but tags are not required
for locked-down environments.

The `agentic` preset includes the `versioning` profile. It creates target repo
`VERSION`, `CHANGELOG.md`, `docs/versioning.md`, and these commands:

```bash
make version-status
make version-check
make agent-changelog-update
make version-bump BUMP=patch
```

`VERSION` and `CHANGELOG.md` are target-owned after creation, so kit updates do
not overwrite the project version history.

If the target repo uses pre-commit hooks:

```bash
pre-commit install
```

To install the test-first executable-spec profile:

```bash
python3 scripts/install.py /path/to/target/repo --profile test-first
```

To compose profiles directly:

```bash
python3 scripts/install.py /path/to/target/repo --profiles review-prompts,test-first
```

To install the experimental API docs-as-tests profile:

```bash
python3 scripts/install.py /path/to/target/repo --profile docs-as-tests
```

To install ignored private context examples:

```bash
python3 scripts/install.py /path/to/target/repo --profile private-context
```

To install stack-aware Node or Python hygiene hints:

```bash
python3 scripts/install.py /path/to/target/repo --profile node
python3 scripts/install.py /path/to/target/repo --profile python
```

## Presets

Presets are the easiest way to install a coherent operating mode:

- `lite`: minimal docs contract plus lite-mode and sidecar-retention guidance,
  without prompt packs or target versioning files.
- `minimal`: documentation contract only.
- `learning`: documentation contract plus review and learning prompts.
- `test-first`: documentation contract plus TDD/executable-spec prompts.
- `agentic`: documentation contract, local agent workflows, review prompts,
  learning prompts, test-first prompts, and local versioning.

The stack-aware `node` and `python` profiles, the experimental `docs-as-tests`
profile, and the privacy-sensitive `private-context` profile are not part of
these presets. Install `node` or `python` explicitly when a target repo wants
managed local stack-hygiene hints without dependency installation or framework
scaffolding. Install `docs-as-tests` explicitly when a repo has local JSON
OpenAPI artifacts and wants declared API doc assertions. Install
`private-context` explicitly when a repo owner wants ignored local context
templates; these opt-in profiles are deliberately absent from default, lite,
minimal, learning, test-first, and agentic installs.

## What gets installed

The kit currently installs:

- `doc-contract.json`
- `AGENTS.md`
- `REVIEW.md`
- `docs/documentation-contract.md`
- `docs/working-rhythm.md`
- `docs/harness-engineering.md`
- `docs/planning-adapters.md`
- `docs/upgrade-flow.md`
- `docs/ops/agent-workflow.md`
- `docs/ops/agent-instruction-hygiene.md`
- `docs/ops/agent-tool-network-allowlist.md`
- `docs/ops/slash-command-grammar.md`
- `docs/adr/0000-template.md`
- `.github/pull_request_template.md`
- `.github/workflows/docs.yml`
- `.github/workflows/docs-contract-comment.yml`
- `.github/workflows/agent-review-readonly.yml`
- `.pre-commit-config.yaml`
- `Makefile` bridge when the target repo does not already have one
- `.doc-contract-kit/make/repo-contract.mk`
- `scripts/_agent_scope.py`
- `scripts/agent_start.py`
- `scripts/agent_task_cleanup.py`
- `scripts/agent_task_prepare.py`
- `scripts/agent_task_status.py`
- `scripts/agent_research.py`
- `scripts/agent_review_run.py`
- `scripts/branch_readiness.py`
- `scripts/check_docs_as_tests.py`
- `scripts/check_doc_impact.py`
- `scripts/classify_review_risk.py`
- `scripts/goal_check.py`
- `scripts/kit_status.py`
- `scripts/lint_agent_docs.py`
- `scripts/localize_doc_impact.py`
- `scripts/render_docs_contract_comment.py`
- `scripts/verify_agent_receipt.py`
- `scripts/version.py`
- `schemas/area-contracts.schema.json`
- `schemas/task-packet.schema.json`
- `.agent-workflows/area-contracts.json`
- `.agent-workflows/instruction-budgets.json`
- `.agent-workflows/schemas/safe-output.schema.json`
- `.agent-workflows/runs/.gitignore`
- `.doc-contract-kit/install.json`
- `.doc-contract-kit/manifest.json`
- `.doc-contract-kit/updates/.gitignore`

The default profile is `minimal`, which keeps target repos portable and does not
assume a local knowledge-base tool.

The `review-prompts` profile also installs:

- `.codex/prompts/multi-agent-repo-review.md`
- `.codex/prompts/codebase-learning-comments.md`
- `.codex/prompts/task-packet.md`
- `.codex/prompts/personas/`
- `.codex/prompts/policies/`
- `.codex/prompts/templates/`
- remediation and verification prompts

The `local-agentic` profile also installs:

- `.agent-workflows/README.md`
- `.agent-workflows/repo-review.md`
- `.agent-workflows/tdd-red-green-receipt.md`
- `.agent-workflows/schemas/session-receipt.schema.json`

Use this profile when the repo must work with local tools only and cannot assume
GitHub Actions, cloud CI, or one specific agent runtime.

Optional runtime adapters can also be installed or updated with
`--runtime-adapter <name>` or `--runtime-adapters <comma-list>`. Supported
adapters are:

- `claude-code`: installs managed `CLAUDE.md`.
- `github-copilot`: installs managed `.github/copilot-instructions.md`.

These files stay thin and point back to `AGENTS.md`, `REVIEW.md`, and scoped
workflow docs. They are recorded in `.doc-contract-kit/manifest.json`, included
in `kit-status`, updated only through explicit install/update commands, and
preserved with conflict reports when customized.

The `versioning` profile also installs:

- `VERSION`
- `CHANGELOG.md`
- `docs/versioning.md`

These files are included by the `agentic` preset. Existing target `VERSION` and
`CHANGELOG.md` files are preserved.

The `private-context` profile also installs:

- `.agent-context/.gitignore`
- `.agent-context/README.md`
- `.agent-context/project-context.example.md`
- `.agent-context/user-preferences.example.md`
- `.agent-context/private-local-context.example.md`

Only README and example guidance are intended to be tracked. The directory
`.gitignore` ignores real local context files by default so accidental `git add`
does not stage private notes. `AGENTS.md` and `REVIEW.md` remain the durable
shared repo instructions. Runtime adapters such as `CLAUDE.md` remain thin
tool-specific pointers. Keryx, Obsidian, or other external memory systems should
be used through their own governed workflows rather than mirrored into this
directory. Secrets belong in approved secret-management tooling, not local
context files.

The `node` profile also installs:

- `.agent-workflows/stack-profiles/node.json`
- `docs/ops/node-stack-profile.md`

Use it when a target repo wants committed local guidance for Node.js command
selection and safety boundaries. The profile asks agents to inspect
`package.json`, committed lockfiles, config files, and existing docs before
running stack commands. It does not install dependencies, create `node_modules`,
generate lockfiles, pick a package manager, scaffold a framework, or contact a
package registry by default.

The `python` profile also installs:

- `.agent-workflows/stack-profiles/python.json`
- `docs/ops/python-stack-profile.md`

Use it when a target repo wants committed local guidance for Python command
selection and safety boundaries. The profile asks agents to inspect
`pyproject.toml`, setup/config files, committed lockfiles, test/lint config, and
existing docs before running stack commands. It does not create virtual
environments, install dependencies, generate lockfiles, choose a build backend,
publish packages, or assume pytest, tox, nox, uv, Poetry, or pip-tools.

## Configuration

`doc-contract.json` lets each target repository customize:

- required documentation contract files
- paths that count as documentation
- ignored paths such as tests
- docs-freshness scope for historical or excluded Markdown
- source paths that imply documentation impact
- expected documentation paths for each impact category

`docs_freshness.historical_paths` marks ADRs, audits, archives, and changelog
history as time-bound records. `make docs-freshness` still checks local links in
those files, but it does not treat documented `make`, `scripts/*.py`, or schema
references there as current executable truth. Use
`docs_freshness.extra_historical_paths` to add target-specific history without
replacing the defaults. Use `docs_freshness.exclude_paths` only for Markdown
that should be skipped entirely by freshness checks.

The checker fails when it detects doc-impacting changes without matching
documentation updates. If a change genuinely needs no docs, the PR body must
include `No docs needed: <reason>`, or CI/local automation must provide
`DOC_CONTRACT_NO_DOCS_NEEDED`. Use
`python3 scripts/check_doc_impact.py --format sarif` or
`python3 scripts/repo_contract_kit.py doc-impact --repo <repo> --format sarif`
when a CI adapter should hand docs-contract findings to Code Scanning.
The installed `.github/workflows/docs-contract-comment.yml` adapter runs the
same docs-impact check on pull requests, renders
`scripts/render_docs_contract_comment.py` Markdown with policy links and next
actions, and upserts one marker comment in the PR conversation.
The installed `docs/ops/slash-command-grammar.md` file defines the future PR
slash-command grammar for `/docs-impact`, `/waive-docs`, `/review-docs`,
`/add-docs`, and `/update-changelog`. It is a spec only: the kit does not yet
execute these comments. Use the local `docs-explain` CLI or
`make agent-docs-explain` to read cited local policy before asking to waive
docs work or request a docs patch. Use `changelog-update` or
`make agent-changelog-update` for release-note proposal/check mode today, and
future hosted implementations must still respect local receipts, sidecar
artifacts, and `.agent-workflows/agent-permission-policy.json`.

The `test-first` profile also installs:

- `.codex/prompts/tdd/`
- `docs/testing-strategy.md`
- `docs/adr/0001-testing-philosophy.md`
- a PR template with test-first evidence checks

Use it when a repository should treat tests as executable documentation for
features, bug fixes, refactors, API contracts, and high-risk cleanup.

The experimental `docs-as-tests` profile also installs:

- `.agent-workflows/docs-as-tests.json`
- `docs/ops/docs-as-tests.md`

Use it only for high-confidence checks declared in JSON. Manifest v2 supports
explicit local OpenAPI operation, response-status, schema-property, and local
JSON key assertions while keeping schema v1 method/path assertions compatible.
The checker refuses missing config, invalid JSON, unsupported assertion kinds,
network URLs, command-like input, missing local artifacts, and missing or
ambiguous selectors. It does not scrape arbitrary Markdown, run fenced examples,
start services, call hosted models, use GitHub APIs, or require non-stdlib
dependencies.

## Installed commands

The maintainer-side CLI can inspect any git repo without requiring an installed
Makefile bridge:

- `python3 scripts/repo_contract_kit.py command-map --json`:
  emit the schema-versioned command catalogue from argparse metadata, including
  flags, JSON support, audience, mutation class, sidecar write behavior,
  aliases, route roles, canonical command pointers, alias groups, route notes,
  examples, exit-code notes, output schema pointers, docs pointers, and
  `json_contract` compatibility metadata for each route. `agent-context --json`
  returns the same catalogue as an agent bootstrap alias.
- `python3 scripts/repo_contract_kit.py agent-tool-manifest --json`:
  emit a command-map-derived local agent manifest with safe commands,
  target-writing commands, sidecar-writing commands, schemas, examples, and
  no-input behavior. The command is read-only metadata and performs no network,
  hosted-model, credential, target-repo, or sidecar writes.
- `python3 scripts/repo_contract_kit.py completion bash|zsh|fish`:
  print shell completion code generated from parser and command-map metadata.
  The command writes only to stdout; redirect it into the shell-specific
  completions path when you want to install it.
- `python3 scripts/repo_contract_kit.py palette --query status --print-command`:
  search commands in an interactive TTY and print exact command previews with
  mutation and write-behavior metadata. The palette does not run commands and
  is disabled for non-TTY, `--no-input`, and `KIT_AGENT=1` runs.
- `python3 scripts/repo_contract_kit.py cli-reference --check docs/cli-reference.md`:
  generate or check the command-map-derived Markdown CLI reference. Use
  `--write docs/cli-reference.md` to refresh it and `--json` to inspect the
  generated command metadata plus Markdown docs-as-tests claims.
- `python3 scripts/repo_contract_kit.py --style pretty doctor --repo /path/to/repo`:
  add restrained ANSI emphasis to selected human summaries. Use `--style plain`
  or `NO_COLOR=1` to force plain text; JSON output is never styled.
- `make cli-ux-fixtures`:
  run fixture-backed regression checks for help lanes, parse-error recovery,
  no-input and agent-mode behavior, compact human summaries, command-map JSON,
  palette non-TTY fallback, and CLI reference freshness. Review guidance lives
  in `docs/cli-ux-regression-fixtures.md`.
- `python3 scripts/repo_contract_kit.py orient --repo /path/to/repo --json`:
  emit startup context, install state, docs-impact state, and next-command
  guidance without writing files.
- `python3 scripts/repo_contract_kit.py status --repo /path/to/repo --json`:
  emit git, target-version, install-manifest, managed-file, local kit
  provenance, and `kit_drift` diagnostics comparing global-tool metadata with
  the target install receipt, source refs, and prompt snapshot. Text mode
  separates running tool, target install, target repo, prompt snapshot, and
  source-ref version roles, then prints safe next commands.
- `python3 scripts/repo_contract_kit.py mode-check --repo /path/to/repo --json`:
  select `lite`, `standard`, or `release-gated` from deterministic local
  triggers, reporting the selected mode, trigger evidence, downgrade blockers,
  and next commands without target or sidecar writes.
- `python3 scripts/repo_contract_kit.py calibration --repo /path/to/repo --json`:
  report local harness outcome fields such as time-to-orient,
  commands-to-green, skipped checks, escalation reasons, false-positive
  disposition, and human burden. Unknown fields stay explicit instead of
  inferred.
- `python3 scripts/repo_contract_kit.py retention --repo /path/to/repo --json`:
  preview local sidecar retention, privacy labels, hosted-model sharing
  warnings, and purge candidates. The command never deletes files by default.
- `python3 scripts/repo_contract_kit.py sidecar-init --repo /path/to/repo --json`:
  create the repo's external sidecar directories and `status.json` without
  writing into the target repo.
- `python3 scripts/repo_contract_kit.py feedback --repo /path/to/repo --message "status recovery was unclear"`:
  append local CLI friction feedback to the sidecar JSONL ledger with repo id,
  tool version, target version, context command, optional last error, tags, and
  privacy metadata. Use `--export-json` or `--list` to read it without sidecar
  or target-repo writes.
- `python3 scripts/repo_contract_kit.py agent-self-heal --repo /path/to/repo --json`:
  preview guarded generated-state recovery, including sidecar initialization
  and stale task metadata or prepare-lock quarantine. Add `--apply` only after
  reviewing the plan; apply writes a sidecar before/after receipt and refuses
  unrelated tracked source changes.
- `python3 scripts/repo_contract_kit.py doc-impact --repo /path/to/repo --working-tree --json`:
  evaluate documentation impact for staged, working-tree, branch, or explicit
  changed files. Use `--format sarif` for Code Scanning compatible output.
- `python3 scripts/repo_contract_kit.py docs-explain --repo /path/to/repo --question "Can we waive docs?" --focus waiver --json`:
  scan local README/docs/policy files, return source paths, headings, line
  snippets, and a ready local prompt without writing target files, sidecar
  files, or calling hosted models/network.
- `python3 scripts/repo_contract_kit.py docs-as-tests --repo /path/to/repo --json`:
  run explicit local docs-as-tests assertions from
  `.agent-workflows/docs-as-tests.json` without target writes or network calls.
- `python3 scripts/repo_contract_kit.py goal-check --repo /path/to/repo --working-tree --json`:
  map changed files to `.agent-workflows/area-contracts.json` and report
  `aligned`, `extends`, `conflict`, or `unknown` states without guessing
  ownership for unmatched paths.
- `python3 scripts/repo_contract_kit.py agent-context-bundle --repo /path/to/repo --json`:
  compose dirty state, backlog/next work, task status, docs impact, goal
  check, token-budget totals, sidecar paths, and readiness hints into a bounded
  startup or handoff bundle with explicit omissions.
- `python3 scripts/repo_contract_kit.py agent-state-ledger --repo /path/to/repo --json`:
  emit a read-only state ledger for dirty checkout state, task metadata and
  worktrees, sidecar availability, preflight/doctor, automation handoff,
  self-heal, finalizer, readiness/final receipt evidence, unresolved blockers,
  local attribution, and deterministic next safe commands. It is an
  index/report only; it does not clean, close out, finalize, hand off, or write
  sidecar receipts.
- `python3 scripts/repo_contract_kit.py branch-readiness --repo /path/to/repo --json`:
  aggregate local branch-or-PR readiness evidence before PR update, merge queue,
  auto-merge, or branch-protection governance. The command checks local git
  state, base/head refs, docs-impact and `No docs needed:` waiver state,
  changelog/version evidence, task readiness when prepared task metadata is
  available, task-status hazards, explicit local CI/check JSON, and optional
  receipt or review-disposition JSON. It reports top-level
  `target_repo_writes=false`, `sidecar_writes=false`, and `network_calls=false`;
  it does not poll GitHub, approve, comment, label, enqueue, merge, or edit
  branch protection. For GitHub branch protection, treat this local report as
  owner-reviewed evidence before a human or hosted workflow updates PR state;
  GitHub still owns required status checks, branch-protection rules, and merge
  queues.
- `python3 scripts/repo_contract_kit.py instruction-diet --repo /path/to/repo --json`:
  audit agent-facing instruction files and propose no-write offload targets for
  budget pressure, duplicated procedures, route-map drift, and stale command
  detail.
- `python3 scripts/repo_contract_kit.py docs-propose --repo /path/to/repo --changed-file cli/new.py --write-sidecar --json`:
  write reviewable docs proposal JSON, Markdown, and patch artifacts under the
  repo sidecar without modifying target files.
- `python3 scripts/repo_contract_kit.py changelog-update --repo /path/to/repo --changed-file cli/new.py --json`:
  propose or check release-note work from docs-impact context without writing
  `VERSION` or `CHANGELOG.md`.
- `python3 scripts/repo_contract_kit.py onboarding-pr --repo /path/to/repo --preset agentic --write-sidecar --json`:
  generate branch, commit, push, and manual PR instructions for reviewable
  repo-contract-kit onboarding without installing files or opening a PR.
- `python3 scripts/repo_contract_kit.py review-plan --repo /path/to/repo --json`:
  emit a read-only review plan for an agent.
- `python3 scripts/repo_contract_kit.py task-packet --repo /path/to/repo ...`:
  emit a task-packet JSON scaffold for a backlog item, issue, finding, decision,
  or human request, including story context and explicit non-goals before the
  work becomes executable.
- `python3 scripts/repo_contract_kit.py verify --repo /path/to/repo --json`:
  combine non-mutating status and docs-impact checks.
- `python3 scripts/repo_contract_kit.py update-plan --repo /path/to/repo --json`:
  emit a non-mutating migration/update plan with install state, sidecar state,
  warnings, blockers, actions, conflicts, and explicit next commands.
- `kit self status` / `kit update --global`:
  inspect or refresh the global tool checkout used by the launcher.
- `kit setup`:
  enroll the current git repo as a target using the globally installed launcher.
- `kit target repair-source-clone`:
  preview or, with `--apply`, remove accidental nested source checkouts before
  enrolling or updating the target repo.
- `kit status` / `kit update`:
  inspect or apply safe managed updates for the current git repo from the global
  tool checkout.
- `python3 scripts/repo_contract_kit.py install --repo /path/to/repo --preset agentic --runtime-adapters claude-code,github-copilot`:
  explicitly install kit files into a target repo from a source checkout.
- `python3 scripts/repo_contract_kit.py migrate-config --repo /path/to/repo --kit /path/to/kit --json`:
  explicitly migrate only installed profile/config metadata schema markers.
- `python3 scripts/repo_contract_kit.py update --repo /path/to/repo --apply --runtime-adapters claude-code,github-copilot --json`:
  explicitly apply safe managed updates from a kit checkout.

For repo-external agent artifacts, pass `--write-sidecar` to `orient`,
`review-plan`, `docs-propose`, `onboarding-pr`, `task-packet`, or `verify`. The
CLI writes under
`${XDG_STATE_HOME:-~/.local/state}/repo-contract-kit/<repo>-<id>/` and reports
the exact paths in `sidecar_writes.paths`; it still does not create
`.agent-workflows/` or `.doc-contract-kit/` in the target repo.

Installed target repos get Makefile entrypoints:

- `make help` / `make workflow-help`: print the orient, review, scope, execute
  rhythm and point to `docs/working-rhythm.md`.
- `make agent-start`: write an ignored local session packet with an agent
  brief, startup context, latest ADR context, review-risk tier, kit/version
  context, task-start freshness diagnostics, recommended prompts/personas, and
  a receipt template. The freshness section reports global kit metadata, target
  install metadata, repo cleanliness, backlog source, and safe update modes
  without applying target or global updates.
- `make goal-check`: report how current changed files map to the repo goal and
  area contracts in `.agent-workflows/area-contracts.json`. Unknown areas are
  warnings; conflict areas are blockers for readiness.
- `make agent-context-bundle`: emit a compact report for agent startup or
  handoff by composing dirty-state, backlog, task-status, docs-impact,
  goal-check, token-budget, sidecar, and readiness-hint signals. Use
  `CONTEXT_BUNDLE_JSON=1` for machine-readable output.
- `make agent-state-ledger`: emit a local read-only ledger of checkout dirt,
  task metadata/worktrees, leases, active overlaps, final receipts, sidecar
  receipt indexes, closeout preview state, unresolved blockers/warnings, and
  next safe commands. Use `STATE_LEDGER_JSON=1` for machine-readable output.
  Task summaries, unresolved blockers, and latest receipt summaries include a
  local-only attribution object when metadata or receipts provide it, otherwise
  attribution is explicit `unknown`. The command reports
  `target_repo_writes=false` and `sidecar_writes=false` and never performs
  cleanup, closeout, finalization, handoff, or sidecar writes.
- `make agent-branch-readiness`: emit a no-write branch-or-PR readiness report
  that aggregates local evidence before humans consider PR update, merge queue,
  auto-merge, or branch-protection changes. Use `BRANCH_READY_JSON=1` for JSON,
  `BRANCH_READY_CHECKS_JSON=<path>` for an explicit local CI/check export,
  `BRANCH_READY_RECEIPT=<path>` for receipt validation, and
  `BRANCH_READY_REVIEW_DISPOSITION_JSON=<path>` for review-disposition evidence.
  It references `agent-task-ready` when prepared task metadata is available but
  does not replace that per-task gate.
- `make kit-status`: show installed kit version, source ref, prompt snapshot
  ref/hash, profiles, runtime adapters, managed manifest status, managed-file
  cleanliness, and target repo version.
- `kit status` / `kit update`:
  preferred global CLI path for inspecting and applying safe managed updates.
- `kit doctor`: run non-mutating diagnostics for dirty
  state, task/worktree state, and safe recovery commands from the global CLI.
- `make kit-status KIT=/path/to/kit`: fallback comparison against
  a local kit checkout when the global CLI is unavailable.
- `make kit-migrate-config KIT=/path/to/kit`: explicitly migrate
  profile/config metadata schema markers without managed-file updates.
- `make kit-update KIT=/path/to/kit`: safely update managed files
  from a newer local kit checkout. Pass
  `RUNTIME_ADAPTERS=claude-code,github-copilot` when adding or changing managed
  runtime adapters.
- `make kit-refresh KIT=/path/to/kit`: fast-forward pull a clean
  local kit checkout, show update status, then run the safe managed update.
- `make kit-update-stack` / `make kit-refresh-stack`: deprecated maintainer
  compatibility shims for the workflow-source checkout. They require
  `STACK_UPDATE_COMPAT=1`; ordinary target repos should use
  `kit status` and `kit update`.
- `make kit-explain`: explain target-repo ownership, kit-managed files, and the
  existing-repo update path.
- `make docs-check`: run the documentation contract checks.
- `make docs-freshness`: check local docs references and verify that
  `docs/cli-reference.md` matches `kit cli-reference`.
- `make cli-ux-fixtures`: run behavior-focused CLI UX regression fixtures for
  human and agent command surfaces.
- `make docs-as-tests`: run the experimental declared docs-as-tests assertions
  from `.agent-workflows/docs-as-tests.json`. This target is separate from
  `docs-check`; use `DOCS_AS_TESTS_JSON=1` for machine-readable output.
- `make agent-docs-lint`: check local agent instruction files for hidden
  Unicode, stale paths, unsafe references, contradictions, and instruction
  budget drift.
- `make agent-instruction-diet`: emit a no-write instruction diet audit with
  proposed offload targets for bulky or duplicated agent-facing detail.
- `make agent-docs-localize`: emit JSON that maps changed files to likely
  documentation impact.
- `make agent-docs-explain`: answer a local docs-policy question with cited
  README/docs/policy snippets and a no-write prompt before waiving docs work or
  asking for `/add-docs`.
- `make agent-docs-propose`: write a sidecar docs-patch proposal with JSON,
  Markdown, and a reviewable `docs.patch` scaffold; it does not modify the
  target checkout.
- `make agent-review`: point the agent at the multi-agent repo review prompt.
- `make agent-run-review AGENT=manual|amp`: generate persona review artifacts,
  or execute them through Amp CLI when `AGENT=amp`.
- `make agent-research-plan`, `make agent-research-run`,
  `make agent-research-synthesize`, and
  `make agent-research-to-task-packet`: create read-only targeted-research
  artifacts when the `review-prompts` profile is installed.
- `make agent-learn`: point the agent at the learner-focused comment prompt.
- `make backlog-status`: report the selected backlog source, mirror sources,
  open/done counts, warnings, and next open item from the portable backlog
  contract.
- `make backlog-check`: fail when the selected backlog source is missing,
  malformed, or contains duplicate stable ids.
- `make agent-next`: combine backlog status, dirty working tree state, and
  active task metadata into one recommended next handoff.
- `make agent-preflight` / `make agent-doctor`: diagnose dirty-state startup
  blockers, registered worktrees, task metadata, sidecar state, and safe
  recovery commands before starting write-capable work. Use
  `PREFLIGHT_JSON=1` for machine-readable output, `PREFLIGHT_STRICT=1` to fail
  on blockers, or `PREFLIGHT_WRITE_SIDECAR=1` to store an external receipt.
  JSON output includes attribution for checkout dirt, sibling-worktree
  blockers, missing-worktree task metadata, active tasks, and blocked local
  automation receipts when available.
- `make agent-self-heal`: preview guarded generated-state repairs. Set
  `SELF_HEAL_APPLY=1` only after reviewing the plan. Apply can initialize the
  sidecar and quarantine stale generated task metadata or stale prepare locks
  with a sidecar receipt; it does not clean source files, stash, reset, delete
  unrecognized untracked files, or remove task worktrees. Use
  `SELF_HEAL_ALLOW_PATHS=<exact-generated-path>` only to record an exact tracked
  generated path that is intentionally dirty during apply.
- `make agent-task-packet`: point the agent at the task-packet prompt for
  backlog items, issues, accepted findings, and broad human requests. The packet
  must expand compact source rows with story context, non-goals, acceptance,
  validation, exact docs and release metadata surfaces, docs-impact, and risk
  before implementation starts.
- `make agent-task-packet-from-backlog BACKLOG_ID=<id>`: emit a
  machine-readable task packet scaffold for a selected backlog row, with a
  default operator story and explicit non-goals that can be overridden by
  `--story-*` and `--non-goal` flags.
- `docs/planning-adapters.md`: examples for mirroring Keryx, Obsidian, issue
  trackers, spreadsheets, or `docs/backlog.md` into one selected local task
  packet without making the kit write external planning state.
- `make agent-task-status`: show active local task metadata, registered
  worktrees, dirty or missing task worktrees, unknown scopes, and active scope
  overlaps, task leases, owners, owner labels, session/thread ids, automation
  ids, and linked final receipts. Use `TASK_STATUS_STRICT=1` to fail on
  coordination hazards.
- `make agent-task-cleanup`: audit existing task worktrees, flag nested
  `*-agent-worktrees` pools, and move nested worktrees into the flat pool only
  when `TASK_CLEANUP_MOVE_NESTED=1 TASK_CLEANUP_APPLY=1` is set.
- `make agent-task-closeout`: preview finished sibling task worktrees that are
  safe to remove. Set `TASK_CLOSEOUT_APPLY=1` to remove eligible worktrees with
  `git worktree remove` without force, `TASK_CLOSEOUT_KEEP=<n>` to retain the
  newest eligible worktrees, or `TASK_CLOSEOUT_OLDER_THAN_DAYS=<n>` to keep a
  recent inspection window. Dirty, missing, unregistered, nested,
  missing-receipt, unknown-scope, active-overlap, and unmerged cases stay
  blocked for manual inspection.
- `make agent-task-prepare TASK=<id> SCOPE=<paths>`: create a
  worktree-per-task branch, local task packet, receipt template, and in-flight
  metadata for an approved write-capable task. The metadata records a run id,
  optional owner/session/thread/automation attribution, heartbeat timestamp,
  lease expiry, active sibling tasks, and overlap warnings. Set
  `TASK_OWNER=<id>`, `TASK_OWNER_LABEL=<label>`,
  `TASK_SESSION_ID=<session>`, `TASK_THREAD_ID=<thread>`, or
  `TASK_AUTOMATION_ID=<automation>` to persist local attribution while
  preserving existing `TASK_OWNER` and `TASK_SESSION_ID` compatibility.
  Dirty-main failures list changed entries and recovery commands; use
  `TASK_PREPARE_JSON=1` for a machine-readable blocker.
  Set `DIRTY_PRIMARY_BASELINE=1` only when preserving pre-existing checkout
  dirt is intentional. That mode records the primary checkout status entries,
  counts, changed files, HEAD, content-sensitive state hash, and receipt
  scaffolding, then `agent-task-ready` / `agent-task-finalize` block if the
  primary checkout changes after the baseline. `ALLOW_DIRTY=1` remains a legacy
  alias for the same baseline mode.
- `make agent-task-ready`: validate one task worktree before PR update or merge
  handoff. It checks actual changed files versus declared scope, branch
  freshness against `BASE_REF`, strict receipt/docs-impact evidence, goal-check
  status, dirty-primary baseline drift, and overlap with other in-progress task
  scopes. Run it from the task worktree or pass `TASK=<id>` from the primary
  checkout. Use `TASK_READY_JSON=1` for a machine-readable readiness report.
- `make agent-task-finalize TASK=<id> TASK_RECEIPT=<path>`: close one prepared
  task through readiness, lifecycle, final status, and closeout-preview steps in
  one operator flow. Set `TASK_FINALIZE_ACTION=block|abandon` for non-passing
  terminal states, `TASK_FINALIZE_SKIP_READY=1` only when readiness is not
  applicable, `TASK_FINALIZE_JSON=1` for a machine-readable finalizer receipt,
  or `TASK_FINALIZE_CLOSEOUT_APPLY=1` to explicitly apply eligible closeout.
- `make agent-automation-handoff`: preserve recurring automation backlog or
  research edits from a linked worktree by writing a sidecar patch and JSON
  receipt. It blocks by default when run from the primary checkout, when an
  `AUTOMATION_HANDOFF_ORIGINAL_ROOT` checkout is dirty, or when changed files
  fall outside backlog/research paths. Use `AUTOMATION_HANDOFF_JSON=1` for a
  machine-readable receipt and `AUTOMATION_HANDOFF_DRY_RUN=1` to validate only.
  When the original checkout already has unrelated local dirt, capture a start
  receipt with `AUTOMATION_HANDOFF_CAPTURE_ORIGINAL_BASELINE=1`, then pass that
  receipt back as `AUTOMATION_HANDOFF_ORIGINAL_BASELINE=<path>` so handoff only
  blocks new original-checkout mutations. Use
  `AUTOMATION_HANDOFF_ALLOW_ORIGINAL_DRIFT=1` only for an intentional override.
- `make agent-task-heartbeat TASK=<id>`: refresh an in-progress task lease.
- `make agent-task-finish TASK=<id> TASK_RECEIPT=<path>`: mark a task done and
  link final receipt evidence.
- `make agent-task-block TASK=<id>` / `make agent-task-abandon TASK=<id>`:
  close work that cannot or should not continue.
- `make agent-task-prune`: preview closed metadata removal; set
  `TASK_LIFECYCLE_APPLY=1` only after reviewing the candidates. This is
  metadata-only; use `agent-task-closeout` for finished sibling worktree
  folders.
- `make agent-token-budget`: estimate token footprint for agent-facing context
  files and optionally fail with `TOKEN_BUDGET_STRICT=1`.
- `make agent-test-first`: point the agent at the TDD/executable-spec prompt chooser.
- `make agent-verify`: run the verification checks currently available in the installed profile.
- `make version-status`: print the target repo version.
- `make version-check`: validate local SemVer.
- `make agent-docs-explain`: explain local docs policy with citations and no
  target, sidecar, `VERSION`, or `CHANGELOG.md` writes.
- `make agent-changelog-update`: propose or check changelog work from
  docs-impact results without writing `VERSION` or `CHANGELOG.md`.
- `make version-bump BUMP=patch|minor|major`: update `VERSION` and add a
  changelog stub.

The installer writes `.doc-contract-kit/install.json` and
`.doc-contract-kit/manifest.json` so later updates can see which profiles or
preset were installed and which files are safe to manage. The compatibility path
keeps existing installations stable even though the public project name is
repo-contract-kit.

## Recommended rollout

1. Start with one test repo.
2. Install the kit.
3. Let an agent make a small change.
4. See what feels useful or annoying.
5. Adjust the templates and iterate.
6. Only later roll it out widely.

## Philosophy

- docs as code
- explicit documentation obligations
- hooks for local feedback
- optional CI adapters, never required for the core local workflow
- ADRs for important architectural decisions
- gentle adoption path for solo developers
- agent-tool agnostic workflow files before tool-specific adapters
- evidence receipts before trusted automation

## Roadmap

See:

- `docs/vision.md`
- `docs/concepts-for-beginners.md`
- `docs/rollout-guide.md`
- `docs/roadmap.md`

## Development

Run the test suite with:

```bash
make workflow-help
make test
make cli-ux-fixtures
make docs-check
make version-check
```

## Development status

This repository is intentionally early and iterative.
The goal is to create a calm, reusable repository operating system for local
agentic software development.

## Public Repository

This repo is published as [BoweyLou/kit](https://github.com/BoweyLou/kit).
