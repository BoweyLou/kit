# Rollout Guide

This guide uses **kit** as the public command. Existing install receipts still
use the `.doc-contract-kit/` directory and `repo-contract-kit` provenance for
compatibility.

For version 1, `repo-contract-kit` is the single workflow-stack repository.
Read [`docs/version-1-consolidation.md`](version-1-consolidation.md) before
changing repository identity, installer URLs, archive policy, or rollback
behavior.

If this is all new to you, adopt it in layers.

Install the global launcher once per machine:

```bash
curl -fsSL https://raw.githubusercontent.com/BoweyLou/kit/main/install.sh | sh
```

The installer provisions `repo-contract-kit/source` under `~/.local/share/` for
the installer, CLI, and in-repo workflow source. Target repos do not receive a
source checkout. Maintainers who still need the legacy external workflow-source
checkout for migration can opt in with:

If another local tool already owns the `kit` command, install with
`--command-name NAME` or `KIT_COMMAND=NAME`; the installer will not overwrite a
non-owned executable.

```bash
curl -fsSL -o /tmp/kit-install.sh https://raw.githubusercontent.com/BoweyLou/kit/main/install.sh
sh /tmp/kit-install.sh --with-workflow
```

That provisions `agent-workflow-kit/source` under `~/.local/share/` for legacy
maintainer migration work only.

Then enroll each repository from inside that repo:

```bash
kit setup
```

Updating is a two-step process. First update the global tool checkout:

```bash
kit update --global
```

Then update each target repo explicitly:

```bash
kit update --dry-run
kit update
```

The separation is deliberate: a global tool update should not silently rewrite
ten or more target repositories. Each target update still uses managed-file
conflict checks and target-owned file boundaries.

Rollback uses the same separation. If a release needs to be backed out, install
the previous global ref with `kit update --global --ref <tag>` or
`install.sh --ref <tag>`, then revert only the affected target-repo managed
update commit after reviewing `.doc-contract-kit/updates/`.

If a target repo accidentally contains a nested source checkout, clean that up
before target enrollment:

```bash
kit target repair-source-clone
kit target repair-source-clone --apply
```

The repair command is preview-first. It removes only detected nested
`repo-contract-kit` or legacy workflow-source directories, refuses to delete the
repo root, and blocks when unrelated target files are dirty.

For third-party or exploratory work, start without installing anything into the
target repo:

```bash
kit orient --repo /path/to/repo --json
kit sidecar-init --repo /path/to/repo --json
kit doc-impact --repo /path/to/repo --working-tree --json
kit doc-impact --repo /path/to/repo --working-tree --format sarif
kit branch-readiness --repo /path/to/repo --json
kit review-plan --repo /path/to/repo --json
kit onboarding-pr --repo /path/to/repo --preset agentic --json
kit update-plan --repo /path/to/repo --json
```

Those CLI commands are non-interactive and write no repo files. Their JSON
includes `target_repo_writes.performed: false` and a `sidecar_state` block with
the repo root, a deterministic repo hash, and paths under
`${XDG_STATE_HOME:-~/.local/state}/repo-contract-kit/`. That sidecar location is
where non-installed agent startup packets, receipts, review artifacts, and task
packets live when a command explicitly writes them outside the target checkout.
The read-only commands report those paths but do not create directories or run
packets. Use `sidecar-init` to create the external state directories, or pass
`--write-sidecar` to `orient`, `review-plan`, `onboarding-pr`, `task-packet`, or
`verify` to write run artifacts outside the target checkout.
`update-plan` also stays non-mutating: it reports whether the repo is
not-installed, sidecar-only, legacy, current, dirty, invalid, customized,
missing managed files, or missing/outdated profile-config metadata before any
install or update command writes to the target.

Use `onboarding-pr` when the owner wants Renovate-style adoption: the CLI
generates branch, install, validation, commit, push, and manual PR text, and
`--write-sidecar` stores a JSON/Markdown review bundle. It does not run the
install, push the branch, or open a pull request.

Move to the install steps below only when the repository owner wants the
contract checked in.

## Suggested order

1. Install the templates only with `kit setup --preset minimal`.
2. Get used to AGENTS.md and the documentation contract.
3. Start running `make docs-check` locally.
4. Add `--preset learning` when you want review and learning prompts in the repo.
5. Add `--preset test-first` or `--preset agentic` when you want executable-spec prompts and local agent workflows.
6. Run `make kit-status`, `kit status`, and
   `make version-check` so the repo has an update, prompt-snapshot, and target
   SemVer baseline.
7. Add runtime adapters only for tools the repo actually uses, for example
   `--runtime-adapters claude-code,github-copilot`.
8. Add `--profile node` or `--profile python` only when the repo wants committed
   stack-hygiene hints for existing Node.js or Python project files.
9. Add `--profile private-context` only when the repo owner wants ignored local
   context templates for agent use.
10. Add `--profile docs-as-tests` only when the repo has local JSON OpenAPI
   specs and explicit API docs assertions to check.
11. Add hooks if you want faster local feedback.
12. Add CI adapters only if your host supports them. The core workflow must still run locally.
13. Later, add generated docs and broader executable doc tests.

The optional `.github/workflows/docs-contract-comment.yml` adapter comments on
pull requests with docs-contract status, policy links, and next actions. It
checks out the base repository policy files, collects changed filenames through
the GitHub API, and does not replace local `make docs-check` verification.
Installed repos also receive `docs/ops/slash-command-grammar.md`, a
specification-only PR slash-command contract for docs-impact, docs waivers,
docs review, docs additions, and changelog updates. The kit does not execute
those commands yet; future adapters must respect local-first receipts and the
installed permission policy.

## Installed command surface

After install, use these target-repo commands:

- `make help`
- `make workflow-help`
- `make agent-start`
- `make goal-check`
- `make agent-context-bundle`
- `make agent-branch-readiness`
- `make kit-status`
- `make kit-explain`
- `kit status`
- `kit update --dry-run`
- `kit update`
- `kit doctor`
- `make docs-check`
- `make docs-as-tests`
- `make agent-docs-lint`
- `make agent-instruction-diet`
- `make agent-docs-localize`
- `make agent-docs-explain`
- `make agent-docs-propose`
- `make agent-review`
- `make agent-run-review AGENT=manual`
- `make agent-learn`
- `make agent-self-heal`
- `make agent-task-packet`
- `make agent-task-prepare TASK=<id> SCOPE=<paths>`
- `make agent-task-ready`
- `make agent-automation-handoff`
- `make agent-test-first`
- `make agent-verify`
- `make agent-changelog-update`
- `make version-status`
- `make version-check`
- `make version-bump BUMP=patch`

The agent commands print the local workflow or prompt path to use. They
deliberately avoid binding the repository to one agent runtime.

Use `make agent-docs-explain` before waiving docs work or asking for a docs
patch when the local policy is unclear. It scans local README/docs/policy files,
returns cited paths, headings, snippets, and a ready prompt, and does not write
target files, sidecar files, `VERSION`, or `CHANGELOG.md`.
Use `make agent-docs-propose` when docs-impact output identifies missing
coverage but the agent should not edit documentation directly. It writes a JSON
receipt, Markdown prompt, and proposed docs patch under the repo sidecar so a
human or follow-up worker can review and apply it deliberately.
Use `make docs-as-tests` only for the experimental profile. It reads
`.agent-workflows/docs-as-tests.json`, checks declared local OpenAPI operation,
response-status, schema-property, and JSON key assertions, and reports refused
or unsupported claims for missing config, invalid JSON, network URLs,
command-like input, unsupported assertion kinds, missing local artifacts, and
missing or ambiguous selectors. It is separate from `make docs-check`,
`docs-freshness`, `docs-propose`, and semantic receipt review.
Use `--profile private-context` only for explicit opt-in local context
templates. The profile installs `.agent-context/` with README and example files
plus a managed `.gitignore` that ignores real local context files by default.
Do not store secrets, tokens, cookies, passwords, private URLs, account
identifiers, customer data, personal messages, medical or financial data, or
proprietary snippets that should not leave the machine there. Before sharing
local context with hosted models, browser tools, GitHub comments, pull
requests, issues, external tickets, or chat tools, reread it and redact it.
Keep durable shared rules in `AGENTS.md`, `REVIEW.md`, or docs; keep runtime
adapters thin; use Keryx, Obsidian, or other memory systems through their own
governed workflows; and keep credentials in approved secret management.
Use `--profile node` or `--profile python` only for explicit opt-in stack
hygiene hints. These profiles install `.agent-workflows/stack-profiles/*.json`
and `docs/ops/*-stack-profile.md` guidance so agents inspect existing project
files before choosing commands. They do not install dependencies, create
`node_modules` or virtual environments, generate lockfiles, scaffold
frameworks, publish packages, or contact package registries by default.
Use `make agent-changelog-update` when docs-impact or versioning context needs
a release-note proposal or strict check. It reports candidate changelog text and
target version-file state without writing `VERSION` or `CHANGELOG.md`.

Use `make agent-branch-readiness` when local evidence needs to be summarized
before a human updates PR state, considers merge queue or auto-merge, or changes
branch-protection governance. The report aggregates local git state, base/head
refs, docs-impact and explicit `No docs needed:` waiver state, changelog/version
evidence, optional local CI/check JSON, strict receipt validation, review
disposition JSON, task-status hazards, and `agent-task-ready` output when a
prepared task matches the branch. It reports `target_repo_writes=false`,
`sidecar_writes=false`, and `network_calls=false`; it does not call GitHub,
comment, approve, label, enqueue, merge, or edit branch protection.

### Merge Governance Examples

GitHub branch protection can require status checks before a protected branch can
be updated, and GitHub's merge queue applies required checks again against the
latest target branch plus queued changes:

- Protected branch and status-check concepts:
  [GitHub protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
  and
  [GitHub status checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks).
- Merge queue concepts:
  [merge queue overview](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/merging-a-pull-request-with-a-merge-queue)
  and
  [merge queue workflow trigger notes](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue).

Use repo-contract-kit as the local evidence layer under those hosted rules, not
as the hosted actor. A typical owner-operated gate is:

```bash
make agent-task-ready TASK=<task-id> TASK_RECEIPT=<receipt.json>
make agent-branch-readiness BRANCH_READY_JSON=1 \
  BRANCH_READY_CHECKS_JSON=.agent-workflows/local-checks.json \
  > .agent-workflows/branch-readiness.json
```

Then the owner reads `branch-readiness.json`. If `result` is `ready`, the owner
can update the PR, approve an auto-merge request, or use GitHub's UI/CLI to add
the PR to a merge queue. repo-contract-kit does not publish a GitHub status,
comment on the PR, approve it, add labels, enqueue/dequeue it, merge it, edit
branch protection, or read credentials.

Use `checks-json` to import local or external check state without giving
repo-contract-kit network access:

```json
{
  "checks": [
    {"name": "docs-check", "required": true, "state": "passed"},
    {"name": "unit", "required": true, "state": "passed"},
    {"name": "flaky-e2e", "advisory": true, "state": "failed"}
  ]
}
```

Required checks block readiness unless they are passing. Advisory checks become
warnings so the owner can decide whether to proceed. If a hosted GitHub status
check is required by branch protection, configure that hosted check in GitHub or
your CI provider; do not treat `agent-branch-readiness` as having published that
status.

For merge queues, keep the handoff explicit:

1. Run local task readiness and branch readiness.
2. Confirm hosted required checks are configured for normal PR and merge-queue
   events; GitHub documents that Actions workflows used as required checks need
   a `merge_group` trigger for merge queues.
3. Let the owner or GitHub-controlled workflow add the PR to the queue.
4. If the queued merge group fails required checks, rerun local readiness after
   fixing the branch; repo-contract-kit still does not remove or requeue the PR.

Use `make workflow-help` first when the command list is unfamiliar. It presents
the everyday rhythm as four moves: orient, review, scope, and execute. The same
model is documented in `docs/working-rhythm.md` inside installed target repos.

Use `make agent-start` first when you want the least friction. It creates an
ignored session packet with the current repo state, docs-impact result, latest
ADR context, review-risk tier, selected trust profile, recommended
prompts/personas, goal-check summary, and a receipt template for the agent's
final evidence.

Use `make goal-check` when an agent needs to map changed files to declared repo
areas before editing. The local contract lives at
`.agent-workflows/area-contracts.json`; unmatched paths stay `unknown` instead
of being guessed from general repo docs.

Use `make agent-context-bundle` when an agent or automation needs a compact
startup or handoff view without rereading every source document. The report
summarizes dirty state, backlog/next work, task status, docs impact, goal
check, token-budget totals, sidecar paths, and readiness hints, and records
explicit omissions when bounded sections are truncated.

Before using browser research, hosted CI adapters, external models, or
write-capable workers, read `docs/ops/agent-tool-network-allowlist.md` and the
selected trust profile in `.agent-workflows/agent-permission-policy.json`.

Use `make agent-run-review AGENT=manual` to turn the latest session packet into
one prompt per selected reviewer plus review-run JSON artifacts. Use
`AGENT=amp` only when Amp CLI is available and you want the wrapper to execute
the read-only personas with `amp --execute --stream-json`.

Use `make agent-task-packet` when a backlog row, issue, accepted finding,
external planning item, or broad request needs to become one executable unit of
work before an agent edits files.
Use `docs/planning-adapters.md` when the source item lives in Keryx, Obsidian,
GitHub Issues, Linear, Jira, a spreadsheet, or another planner. Keep that
system as the priority source, mirror only the selected local handoff fields,
and stop before implementation if the mirror conflicts with the planner.

Use `make agent-task-status` before launching or handing off parallel
write-capable tasks. It reads the ignored task registry, compares it to `git
worktree list`, and reports dirty or missing task worktrees, unknown active
scopes, untracked task worktrees, and active scope overlaps.

Use `make agent-task-ready` from the task worktree before opening or updating a
PR, or before handing the branch back for merge. It compares actual changed
files to the declared task scope, reports goal-check status, checks base-branch
freshness, validates the task receipt in strict mode, and blocks overlap with
other active task scopes. Set `BASE_REF=<branch>` when the default branch
cannot be inferred locally.
After that per-task gate passes, use `make agent-branch-readiness
BRANCH_READY_JSON=1` when the whole branch or PR needs one local JSON decision
that also includes explicit CI/check, review, receipt, docs-waiver, and
changelog/version disposition.

Use `make agent-automation-handoff` from a disposable automation worktree when a
recurring job has accepted backlog or research edits that need to survive
cleanup without touching the original checkout. It writes a patch and JSON
receipt under the repo sidecar, requires a linked worktree by default, can check
`AUTOMATION_HANDOFF_ORIGINAL_ROOT=<path>` stayed clean, and blocks changed files
outside backlog/research paths. If the original checkout starts dirty, capture a
baseline receipt first, then pass it as
`AUTOMATION_HANDOFF_ORIGINAL_BASELINE=<path>` during final handoff so only new
original-checkout mutations block the automation receipt.

Use `make agent-task-cleanup` when a repo already has messy task worktrees. It
audits the registered layout and is read-only by default. To move nested task
worktrees back into the primary checkout's flat sibling pool, rerun it with
`TASK_CLEANUP_MOVE_NESTED=1 TASK_CLEANUP_APPLY=1`.

Use `make agent-self-heal` when startup is blocked by low-risk generated state.
It previews by default, can initialize sidecar state, and can quarantine stale
generated task metadata or stale prepare locks only with `SELF_HEAL_APPLY=1`.
It writes a sidecar receipt on apply and is not a source cleanup, stash/reset,
untracked-file deletion, or task-worktree removal command.

Use `make agent-task-closeout` when finished sibling task folders should be
reclaimed. It is read-only by default, requires clean terminal task metadata
with durable final receipt evidence, blocks unmerged or active-overlap cases,
and only removes eligible worktrees when `TASK_CLOSEOUT_APPLY=1` is set. Use
`TASK_CLOSEOUT_KEEP=<n>` or `TASK_CLOSEOUT_OLDER_THAN_DAYS=<n>` to retain a
recent inspection window.

Use `make agent-task-prepare TASK=<id> SCOPE=<paths>` after the task packet is
approved and before a write-capable worker edits files. It creates a
`codex/task-...` branch in a sibling worktree, writes local task artifacts, and
records in-flight metadata so overlapping task scopes can warn or block. Run it
from the primary checkout; it refuses to run from an existing task worktree so
new tasks do not create nested worktree pools.

Use `make kit-status` when returning to a repo after some time. It shows the
installed kit version, source ref, selected profiles, workflow prompt snapshot
ref/hash, target repo version, whether the managed manifest exists, and whether
managed files are clean.

Use `make kit-explain` when a repo looks like the kit has become part of the
product code. It explains that the target repo owns the root `Makefile`, while
kit targets live in `.doc-contract-kit/make/repo-contract.mk` and are exposed by
an include line.

Use `kit status` when you want an explicit
`current`/`available` update signal for both the install kit and the prompt
snapshot. Use `kit update --dry-run` before
`kit update`. The updater is plan-first, clean managed
files are updated automatically only on apply, customized files are preserved,
and proposed replacements are written under `.doc-contract-kit/updates/` for
review. If the repo is a legacy install without a manifest, the first apply run
adopts current hashes without overwriting files.
Use `docs/upgrade-flow.md` in installed repos as the operator checklist for the
whole sequence: status, dry run, conflict review, metadata-only migration when
needed, managed update, doctor, and verification. The flow keeps root
`AGENTS.md` in place and treats proposed replacements as review artifacts.
Use the migration command named by the dry run when the plan only needs to stamp
or refresh `profile_config_schema_version` in install metadata. That
metadata-only apply path updates `.doc-contract-kit/install.json` and
`.doc-contract-kit/manifest.json` without rewriting target-owned files, managed
files, or customized managed-file conflict baselines.
Pass `RUNTIME_ADAPTERS=claude-code,github-copilot` when an installed repo should
also gain or keep managed runtime-specific instruction files.
Older clean kit-managed root Makefiles migrate to a target-owned bridge during
update; customized root Makefiles are preserved with a proposed bridge under the
same updates directory.
Each plan and update report includes `read_next` guidance for the target
instructions, installed workflow docs, and the source kit changelog so the
upgrade path is visible at the moment of update.
Update plans and reports also include `after_update` sidecar commands. For
repos updated to a sidecar-capable kit version, run `sidecar-init` once and use
`--write-sidecar` on future `orient`, `review-plan`, `task-packet`, and `verify`
runs when generated agent artifacts should stay out of the target checkout. The
updater does not automatically migrate existing `.agent-workflows/runs/`,
`.agent-workflows/tasks/`, or `.doc-contract-kit/updates/` artifacts; review
them first, then archive or move them deliberately.

When the global CLI is unavailable, the legacy fallback is
`make kit-status KIT=/path/to/kit` followed by
`make kit-update KIT=/path/to/kit`, or
`make kit-refresh KIT=/path/to/kit` when that local kit checkout
should be refreshed from git first.

Do not use stack-update commands for ordinary target-repo rollout. If a
maintainer still needs the deprecated workflow-source compatibility path, run it
from a source workspace with `STACK_UPDATE_COMPAT=1`; new target repos should
stay on the global `kit setup/status/update/doctor` commands.

The `agentic` preset includes the `versioning` profile. That profile creates
local SemVer files when missing and keeps `VERSION` and
`CHANGELOG.md` target-owned so updates never overwrite project release history.

## Start small

Pick one repository first.
Do not attempt to standardize everything at once.

## Expect iteration

The first version will probably be too weak in some places and too strict in others.
That is normal.
The point of repo-contract-kit is to give you a versioned place to improve the
system.
