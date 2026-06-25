# Agent Workflow Stack

Use this page when maintainer work makes it unclear whether a change belongs in
`kit/workflows/`, the install/update layer, or a target repo that
has the kit installed.

The public product surface is the `kit` command. Target-repo operators should
not need to understand or clone a separate workflow-source checkout.

```bash
curl -fsSL https://raw.githubusercontent.com/BoweyLou/kit/main/install.sh | sh
kit setup
kit status
kit mode-check --json
kit task-packet --harness-mode auto --json
kit verify --harness-mode auto --json
kit update --dry-run
```

This repo owns both the install layer and the canonical workflow source. Prompt,
schema, persona, research, TDD, and synthesis source files live under
`workflows/`; installed target repos receive generated template copies through
normal `kit update` flows.

For the version 1 repository identity, archive policy for the old
`agent-workflow-kit` / `Codex_CodeReview` path, compatibility requirements, and
rollback path, use
[`docs/version-1-consolidation.md`](version-1-consolidation.md).

For the installed harness view of the same stack, use
[`docs/harness-engineering.md`](harness-engineering.md). The stack map answers
"which repo owns this?", while the harness map answers "what agent behavior does
this installed surface shape and how do we verify it?"

## Layers

| Layer | Location | Owns | Handoff |
| --- | --- | --- | --- |
| Workflow source | `kit/workflows/` | Canonical prompts, personas, schemas, task-packet guidance, research workflows, generated adapter source, and source-side docs. | Run `make workflow-source-export`, `make workflow-source-check`, then ship through a normal kit update. |
| Install layer | `kit` | Installer profiles, managed templates, optional runtime adapters, update/conflict behavior, the kit-owned make fragment, docs-contract scripts, linting, startup packets, receipts, and installed provenance. | Install or update target repos with `kit setup/status/update`. |
| Installed target repo | Any repo with this kit installed | Day-to-day local workflow commands and repository-specific docs/version decisions. | Report drift with `make kit-status` or `kit status`; apply explicit updates with `kit update`. |

Keep target-facing behavior simple. The link between source and install is a
recorded `workflow-source` snapshot and an explicit update command, not a
runtime dependency on another repo.

## Change Routing

| Change | Start in | Also check | Done when |
| --- | --- | --- | --- |
| Prompt, persona, TDD, research, synthesis, or schema source changes | `workflows/` | Whether generated target templates and target-facing docs need refresh. | `make workflow-source-export`, `make workflow-source-check`, install/update tests, `CHANGELOG.md`, and `VERSION` are current. |
| Installed Make targets, scripts, templates, profiles, manifests, or update behavior | `kit` | Whether `workflows/` source or target docs also need a clarification. | Install/update tests pass, `CHANGELOG.md` and `VERSION` are current, and target docs explain the command. |
| Target-repo operator confusion | `kit` CLI/docs/templates | Whether the target repo has local overrides that should stay target-owned. | The global CLI, `docs/working-rhythm.md`, `.agent-workflows/README.md`, or `make workflow-help` points to the next command without requiring knowledge of old source repos. |
| Release or provenance pairing | `kit` | `kit status` in targets and `make workflow-source-check` in this repo. | The target records the installed kit version/ref and `workflow-source` prompt snapshot. |

## Installed Target Guidance

An installed target repo normally needs only one checkout: the target repo
itself. Prefer the global CLI for management:

```bash
kit status
kit mode-check --json
kit task-packet --harness-mode auto --json
kit verify --harness-mode auto --json
kit update --dry-run
```

Inside the target repo, installed Make targets remain available for local work:

```bash
make workflow-help
make agent-start
make kit-status
make kit-explain
```

If the local kit checkout is available, legacy Makefile flows can still compare
and update explicitly:

```bash
make kit-status KIT=/path/to/kit
python3 /path/to/kit/scripts/repo_contract_kit.py update-plan --repo "$(pwd)" --json
make kit-update KIT=/path/to/kit
make kit-refresh KIT=/path/to/kit
```

When a target repo needs runtime-specific instruction files, select thin
adapters explicitly:

```bash
kit update --runtime-adapters claude-code,github-copilot
```

Those adapters are installed target-repo surfaces owned by this kit. Their job
is only to route Claude Code or GitHub Copilot back to `AGENTS.md`, `REVIEW.md`,
and scoped workflow docs.

The update script is plan-only unless it receives an explicit apply flag.
`update-plan` emits the agent-readable migration/update plan without writing
target files. Installed `kit-update` applies files from the local checkout by
passing the apply flag. `kit-refresh` first verifies that the local checkout is
clean, pulls it fast-forward, then runs the same safe update path.

The target repo owns the root `Makefile`. The installed kit make targets live in
`.doc-contract-kit/make/repo-contract.mk`; the root `Makefile` should include
that fragment when the target wants `make agent-start`, `make kit-status`, and
the other kit commands. Existing customized Makefiles are preserved during
updates.

## Release Pairing

Keep releases single-product:

- kit version means either the installer, installed target-repo
  surface, or in-repo workflow source changed.
- each installed target records the kit version/ref and the
  computed `workflow-source` prompt snapshot.
- legacy receipts that mention `agent-workflow-kit` remain readable for status
  and update migration, but new installs should not require that repo.
- version 1 uses this repository, this installer, this CLI, and this
  `VERSION` / `CHANGELOG.md` stream; do not introduce a second normal release
  path.

Do not make target repos fetch a workflow-source repo at runtime. If prompt
source changes need to reach targets, export the generated templates in this
repo and ship them through a normal kit update.
