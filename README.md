# kit

`kit` installs and maintains repository operating contracts: docs checks,
agent instructions, local workflow commands, receipts, task packets, and safe
update metadata.

Use it when a repo needs a repeatable local way for humans and coding agents to
understand what changed, which docs are affected, what checks matter, and how to
update shared workflow files without overwriting repo-owned work.

## Start Here

Install the global launcher once:

```bash
curl -fsSL https://raw.githubusercontent.com/BoweyLou/kit/main/install.sh | sh
```

Then enroll a target repo:

```bash
cd /path/to/repo
kit start              # choose the route and apply any local-safe kit update
kit setup --preset lite
kit status
```

Use `agentic` instead of `lite` when agents will regularly review, plan, edit,
or verify the repo:

```bash
kit setup --preset agentic
```

`kit setup` is a two-word command. Do not look for a separate `kit-setup`
script.

## Which Mode?

| Situation | Use | Why |
| --- | --- | --- |
| Small repo, local maintenance, narrow docs or low-risk work | `lite` | Short path with deterministic escalation. |
| Normal implementation work, backlog items, review findings, or multi-file edits | `standard` | Full task packet, docs impact, and validation evidence. |
| Public CLI/API/config/schema, installer/update behavior, security/privacy, generated docs, `VERSION`, or `CHANGELOG.md` | `release-gated` | Explicit release and compatibility evidence. |

Let the tool choose when unsure:

```bash
kit start
kit start --lite
kit start --no-update
kit mode-check --json
```

Read [docs/lite-mode.md](docs/lite-mode.md) for the full mode contract.

## Human Daily Path

For a target repo with kit installed:

```bash
kit start
kit status
kit mode-check
kit update --dry-run
kit doctor
kit closeout-plan
```

`kit start` is the front door. In an installed target repo it first checks the
already-local kit checkout and applies only safe managed-file or kit-metadata
updates when there are no blockers or customized-file conflicts. Use
`kit start --no-update` to skip that check or
`kit start --update-policy check-only` to report the local update plan without
writing.

When an update plan looks right:

```bash
kit update
```

Remote/global updates remain explicit: run `kit update --global` to refresh the
tool checkout, and `kit update` to apply a target update yourself. Kit updates
preserve target-owned files and customized managed files. Proposed replacements
are written under `.doc-contract-kit/updates/` for review.

Successful `kit setup` and `kit update` runs register enrolled targets in local
kit state. To import existing primary repos without pulling in old task
worktrees, run:

```bash
kit target import --root /Volumes/Myrtle/Code/04_Code --dry-run
```

Then inspect scope with `kit target list --json` and check dirty targets before
planning a batch update:

```bash
kit target dirty-report --json
```

To preview every registered target repo, run:

```bash
kit update --all --dry-run
```

To apply updates across registered targets, use `kit update --all --apply`.
Batch dry-run classifies dirty targets before update planning, and batch apply
skips dirty, missing, or no-longer-enrolled targets instead of rewriting them.
If the dry-run reports stale missing registry entries, clean them with
`kit target prune-missing --dry-run` and then
`kit target prune-missing --apply`.

Disposable task worktrees use a separate lane:

```bash
kit worktree audit --root /Volumes/Myrtle/MiniProjects/MiniCommand --json
kit worktree prune --root /Volumes/Myrtle/MiniProjects/MiniCommand --dry-run
```

`--root` may be either an exact repo root or a parent directory. Exact Git repo
roots also inspect the repo's linked sibling worktrees, such as
`MiniCommand-agent-worktrees/...`.

Read [docs/human-guide.md](docs/human-guide.md) for install, daily use, update,
and troubleshooting flows.

## Agent Daily Path

Agents should not scrape this README for command semantics. Use structured
entrypoints:

```bash
kit start --json              # first route selector; may local-safe update
kit start --no-update --json  # no-write startup payload
kit command-map --json        # command safety and schemas
kit agent-tool-manifest --json
kit agent-context --json      # compatibility alias for command-map metadata
kit mode-check --json
```

In an installed target repo, `make agent-start` remains the local startup packet
lane. Use `make agent-context-bundle` when a handoff needs compact repo context.

For normal scoped work:

```bash
kit task-packet --harness-mode auto --json
kit verify --harness-mode auto --json
kit closeout-plan --json
```

Run `kit closeout-plan --json` before claiming implementation work is done. If
`can_claim_done` is false, report the `completion_state` and `next_action`
instead of saying the work is closed out.

`closeout-plan` also embeds the repo-aware disposable-worktree audit. When
`worktree_prune.summary.would_remove` is non-zero, run the reported
`kit worktree prune --root <repo> --dry-run --json` path before working through
task-ledger blockers. Dirty worktrees remain blocked and are listed in
`worktree_prune.blocked`.

Treat `git_worktree_state` and `kit_managed_state` as separate facts. A Git
dirty checkout needs integration or a receipt. Kit managed-file proposals under
`.doc-contract-kit/updates/` need review, but they are not Git worktree dirt.
When preparing a dirty-baseline task, commit or park untracked source files
inside the task scope first; a fresh task worktree starts from `HEAD` and will
not contain those files.

Use JSON fields such as `target_repo_writes`, `sidecar_writes`, `route_role`,
`audience`, `output_schema`, and `next_commands` to decide whether a command is
safe, mutating, human-facing, or agent-only.

Read [docs/agent-guide.md](docs/agent-guide.md) for the machine contract.

## What Kit Installs

Depending on the preset, kit can install:

- root `AGENTS.md` and `REVIEW.md`
- documentation impact and freshness checks
- local Make targets for agent startup, review, task packets, and verification
- `.agent-workflows/` policies, schemas, receipts, and task metadata
- optional Codex, Claude Code, and GitHub Copilot prompt adapters
- safe managed update metadata under `.doc-contract-kit/`

Read [docs/capabilities.md](docs/capabilities.md) for the capability map.

## Optional macOS Companion

Kit Companion is a separate, optional menu-bar app for local status visibility.
It is not required for setup, updates, reviews, agents, or any normal kit
workflow. The CLI remains complete and authoritative without it.

The app runs read-only JSON commands such as `kit target dirty-report --json`
and `kit closeout-plan --json`, shows registered repo health, and copies next
commands for terminal use. Mutating actions stay in Terminal.

Build it only when wanted:

```bash
make macos-build
make macos-dmg
```

Read [docs/macos-companion.md](docs/macos-companion.md) for the optional install
and safety boundary.

## Maintainers

This repository owns both the install layer and the canonical workflow source:

- implementation, installer, updater, templates, and tests live at the root
- workflow prompts, personas, schemas, and generated adapter source live under
  `workflows/`
- historical `agent-workflow-kit` / `Codex_CodeReview` material is archived
  under `archive/agent-workflow-kit/`

Maintainer checks:

```bash
make workflow-source-check
make docs-freshness
make docs-check
make version-check
make test
```

Read [docs/maintainer-guide.md](docs/maintainer-guide.md) and
[docs/agent-workflow-stack.md](docs/agent-workflow-stack.md) before changing
source ownership, release behavior, or generated workflow material.

For the version 1 repository identity, archive policy, compatibility gate, and
rollback path, read
[docs/version-1-consolidation.md](docs/version-1-consolidation.md).

## Command Reference

The command reference is generated from the CLI metadata:

- [docs/cli-reference.md](docs/cli-reference.md)
- `kit command-map --json`
- `kit cli-reference --check docs/cli-reference.md`

Prefer the generated reference for exact flags, JSON schemas, route roles, and
mutation metadata.

## Public Repository

[BoweyLou/kit](https://github.com/BoweyLou/kit)
