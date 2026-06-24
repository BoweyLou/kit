# Agent Workflow Stack

Use this page when the relationship between this legacy source checkout,
`repo-contract-kit`, and installed target repositories starts to blur.

The operator-facing product is `repo-contract-kit`. New target repos should not
need to understand or clone this workflow-source repo. The normal path is:

```bash
curl -fsSL https://raw.githubusercontent.com/BoweyLou/repo-contract-kit/main/install.sh | sh
kit setup --preset agentic
kit status
kit update
kit doctor
```

`kit setup` is a two-word command: the installed launcher is `kit`, and `setup`
is its subcommand. Agents should resolve `kit` from `PATH` rather than searching
this checkout for a `kit-setup` script.

For the harness view of the same stack, use
[`docs/harness-engineering.md`](harness-engineering.md). The stack map answers
"which repo owns this?", while the harness map answers "what agent behavior does
this component shape and how do we verify it?"
For runtime-specific artifact support, use
[`docs/runtime-compatibility.md`](runtime-compatibility.md).

`AGW-100` moved the canonical workflow source into
`repo-contract-kit/workflows/`. This checkout is now a legacy history and
migration source; use it only for archive validation, source diffs, or
recovering historical context.

## Layers

| Layer | Repo or location | Owns | Does not own |
| --- | --- | --- | --- |
| Workflow source | `repo-contract-kit/workflows/` | Canonical prompts, personas, schemas, task-packet guidance, research workflows, generated adapter source, and source docs. | Target-repo product code or target-specific local overrides. |
| Legacy source history | this checkout | Historical prompts, scripts, regression fixtures, backlog evidence, and migration comparison material until archive closeout. | New canonical workflow-source edits. |
| Install layer | `repo-contract-kit` | The public product surface: global installer, target enrollment, target status/update/doctor, installer profiles, template files, managed update behavior, target-repo Make targets, docs-contract scripts, instruction linting, startup packets, receipts, and workflow prompt snapshots. | Target-repo product code or local release history. |
| Installed target repo | Any repo with the kit installed | Day-to-day commands such as `make agent-start`, `make kit-status`, `make agent-task-packet`, `make agent-task-prepare`, and `make agent-verify`. | Shared prompt-library or installer design decisions. |

Do not expose legacy source history to target-repo operators. Normal target
maintenance uses the global `kit setup/status/update/doctor` commands.

## Change Routing

| Change | Start in | Also check | Done when |
| --- | --- | --- | --- |
| Prompt, persona, TDD, research, synthesis, or schema source changes | `repo-contract-kit/workflows/` | Whether generated target templates and target-facing docs need refresh. | The workflow-source export/check targets, install/update tests, and docs/version checks pass in `repo-contract-kit`. |
| Installed Make targets, update behavior, installer profiles, target-repo scripts, or manifest handling | `repo-contract-kit` | Whether workflow source or target docs should describe the new workflow. | Install/update tests pass and target-repo docs explain the command. |
| Confusion in target-repo operator flow | `repo-contract-kit` | Whether this legacy source repo still says something misleading. | The global CLI, `docs/working-rhythm.md`, or installed `.agent-workflows/README.md` points to the right next command without requiring knowledge of two source repos. |
| Legacy archive cleanup | this checkout | Whether `repo-contract-kit/workflows/` has the needed source material. | Archive/read-only guidance is clear and no normal workflow starts here. |

## Consolidation Direction

`AGW-100` is the tracked consolidation item. It makes `repo-contract-kit` the
only normal documented surface and treats this checkout as legacy history until
archive closeout.

The preferred end state is:

- one public installer command
- one global `repo-contract-kit` CLI
- one per-repo enrollment command
- target repos receive generated guardrails and provenance, not nested source
  checkouts
- source-maintainer details live under `repo-contract-kit/workflows/`

## Four Linking Moves

### 1. Maintainer Stack Map

During the archive window, maintainer docs should answer one question: "Is this
historical context, or does the live change belong in `repo-contract-kit`?"

In this repo, this page is the legacy source-side map. In `repo-contract-kit`,
the matching maintainer doc describes the live workflow source and installer
surface.

### 2. Decision Table

The routing table above is the compact rule. It is intentionally more useful
than a long conceptual explanation because it starts from the change the
operator is trying to make.

When a task needs historical material from this checkout, record that as
migration evidence for the `repo-contract-kit` task rather than creating a new
normal source-edit path here.

### 3. Stack Status

Legacy coordination can still use:

```bash
make stack-status KIT=/path/to/repo-contract-kit
```

The command prints:

- this source repo's version, git state, and `make self-check` result
- the kit checkout's version and git state
- the installed `repo-contract-kit` and workflow prompt snapshot
  recorded in this source repo's `.doc-contract-kit/` metadata

Use `make kit-status` inside ordinary target repos. Use `make stack-status`
from this source repo only when validating archive/migration state.

### 4. Single Product Releases

Keep release work in `repo-contract-kit`:

- `repo-contract-kit` version means the installer, target-repo surface, or
  workflow source changed.
- an installed target repo records the installed `repo-contract-kit`
  version/ref and the workflow prompt snapshot.

The practical release flow is:

1. Change and validate `repo-contract-kit`.
2. If historical material from this checkout was needed, record that evidence in
   the `repo-contract-kit` change.
3. In target repos, run `kit status`, then `kit update --dry-run`, then
   `kit update`. Use `kit doctor` for non-mutating diagnostics.

Do not make `kit-update` part of ordinary validation. Updates should be visible,
reviewable maintenance actions. Local `make kit-update
KIT=/path/to/repo-contract-kit` flows remain fallback paths when the global CLI is
not available.
