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
kit mode-check --json
```

Read [docs/lite-mode.md](docs/lite-mode.md) for the full mode contract.

## Human Daily Path

For a target repo with kit installed:

```bash
kit status
kit mode-check
kit update --dry-run
kit doctor
```

When an update plan looks right:

```bash
kit update
```

Kit updates preserve target-owned files and customized managed files. Proposed
replacements are written under `.doc-contract-kit/updates/` for review.

Read [docs/human-guide.md](docs/human-guide.md) for install, daily use, update,
and troubleshooting flows.

## Agent Daily Path

Agents should not scrape this README for command semantics. Use structured
entrypoints:

```bash
kit agent-context --json
kit command-map --json
kit agent-tool-manifest --json
kit mode-check --json
```

For normal scoped work:

```bash
kit task-packet --harness-mode auto --json
kit verify --harness-mode auto --json
```

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
