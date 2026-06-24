# Runtime Adapters

This is legacy source-checkout documentation. Current workflow-source edits
belong in `repo-contract-kit/workflows/`; this checkout keeps historical
runtime-adapter context, archive validation material, and migration evidence.
Runtime-specific files are still projections from a tool-neutral workflow
source, but the live source now lives in `repo-contract-kit`.

For the runtime-by-runtime support matrix, current/planned/manual-only status,
validation sources, and privacy notes, see
[`docs/runtime-compatibility.md`](runtime-compatibility.md).

## Current Source Routing

- In the live stack, `repo-contract-kit/workflows/manifest.json` records the
  prompt source, generated adapters, planned adapters, and installer boundary.
- In the live stack, `repo-contract-kit/workflows/prompts/` contains the
  Markdown and JSON prompt assets.
- In this checkout, `workflows/manifest.json`, `workflows/prompts/`,
  `.codex/prompts/`, `.github/copilot-instructions.md`, and
  `dist/codex-skill-pack/` are historical or generated archive material used for
  migration comparison and validation.

Do not hand-edit generated adapter outputs as the source of truth. For current
runtime-adapter work, edit `repo-contract-kit/workflows/`, then run the
workflow-source export/check and validation commands in `repo-contract-kit`.
For archive maintenance in this checkout only, edit `workflows/prompts/` or
`workflows/manifest.json`, then run:

```bash
make prompt-adapters-export
make prompt-adapters-check
```

`make validate` also runs the adapter sync check.

Adding a new live prompt is source work in `repo-contract-kit/workflows/`.
Historical prompt files such as `workflows/prompts/maintainer-queue.md` in this
checkout should be changed only for archive or migration maintenance.
Runtime-specific copies are generated artifacts and should be refreshed instead
of edited directly.

Local-model compatibility notes are runtime guidance, not adapter support.
Use [`docs/runtime-compatibility.md`](runtime-compatibility.md) before running a
review-only local or self-hosted model pass, then record the actual data
boundary, model/provider expectations, caveats, and escalation decision in the
receipt. Do not add a generated adapter merely because a runtime can call
Ollama, a self-hosted endpoint, or an OpenAI-compatible API.

## Codex Skill Pack

Codex skills are directories with a required `SKILL.md` plus optional bundled
resources. `agent-workflow-kit` exports selected workflow prompts into that
shape without installing them into the user's Codex home:

```bash
make skill-pack-export
make skill-pack-check
make skill-pack-list
```

The default artifact root is `dist/codex-skill-pack/`. It contains one folder
per skill and a deterministic `pack-manifest.json` with the source version,
source files, generated files, byte counts, and SHA-256 hashes. The current
export set is declared in `workflows/manifest.json` under
`codex_skill_pack.skills` for archive validation. Current export-set changes
belong in `repo-contract-kit/workflows/manifest.json`.

Use `SKILL_PACK_OUTPUT=/path/to/pack` when a CI job, release task, or local
experiment needs the artifact somewhere else. Use
`SKILL_PACK_SKILLS="review task-packet"` to export a subset by skill id or
skill name.

To install manually for one repository, copy or symlink the generated skill
directories into that repository's `.agents/skills/` directory. To install for a
single user, copy or symlink them into `$HOME/.agents/skills/`. The exporter
does not write either location unless the caller explicitly sets
`SKILL_PACK_OUTPUT` there.

## Adapter Selection

Adapter selection belongs in the install/update layer, not in every agent
startup. `repo-contract-kit` should install selected projections into target
repositories with a future interface like:

```bash
repo-contract-kit install --preset agentic --adapters codex,claude,cursor
repo-contract-kit update --adapters codex,claude,cursor
```

Startup should choose an active agent for the session packet only, for example:

```bash
make agent-start AGENT=codex
make agent-start AGENT=claude
```

That startup command should read installed files and generate session context;
it should not rewrite repo policy files on every run.

Before adapter work starts, check the live `repo-contract-kit` checkout and this
legacy checkout if historical comparison is needed. `repo-contract-kit/workflows/`
owns the current source and generated adapter definitions; `repo-contract-kit`
also owns installer flags, target-repo writes, update behavior, and generated
files inside installed repositories.

## Current And Planned Adapters

Current generated adapters:

- `codex` -> `.codex/prompts/`
- `copilot` -> `.github/copilot-instructions.md`

Current Codex skill-pack exports:

- `review` -> `agent-workflow-review`
- `task-packet` -> `agent-workflow-task-packet`
- `implementation` -> `agent-workflow-implementation`
- `tdd` -> `agent-workflow-tdd`
- `research` -> `agent-workflow-research`
- `learning-comments` -> `agent-workflow-learning-comments`

Planned adapters are recorded in `repo-contract-kit/workflows/manifest.json`;
the local `workflows/manifest.json` copy is historical:

- `claude` -> `CLAUDE.md`, `.claude/commands/`
- `cursor` -> `.cursor/rules/*.mdc`
- `continue` -> `.continue/rules/*.md`
- `windsurf` -> `.windsurf/rules/`
- `plain` -> `.agent-workflows/`

The next implementation should wire adapter selection through
`repo-contract-kit` or add another runtime projection from the same source.
Use the compatibility matrix before adding a projection so manual-only and
unsupported runtime surfaces do not look like supported adapters.
