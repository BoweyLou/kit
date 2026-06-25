# AGENTS.md

## Purpose

`kit` is the single source repository for the installable repository contract
tool and its workflow source.

Keep the root README short. Put detailed operational rules in scoped docs,
schemas, generated references, or tests.

## Start Here

1. Read `README.md` for the human front door.
2. Read `docs/agent-guide.md` before driving the repo as an agent.
3. Read `docs/maintainer-guide.md` before changing installer, updater,
   templates, workflow source, generated docs, versioning, or archive policy.
4. Use `kit command-map --json` and `kit agent-tool-manifest --json` for
   machine-readable command metadata. Do not infer command safety from prose.

## Source Boundaries

- Root `scripts/`, `templates/`, `install.sh`, tests, and docs own the product
  implementation and installed target-repo surface.
- `workflows/` owns canonical prompts, personas, workflow schemas, and source
  material that can be exported into installed profiles.
- `archive/agent-workflow-kit/` is read-only historical material. Do not start
  normal work there.

## Documentation Contract

If a change affects public CLI behavior, installer/update behavior, profiles,
templates, schemas, workflow source, generated docs, versioning, or the
human/agent operating model, update the relevant docs in the same change.

If no docs are needed, say why in the final summary.

## Checks

Before finishing normal changes, run the smallest relevant set:

```bash
make docs-check
make docs-freshness
make workflow-source-check
make version-check
make test
```

For docs-only structure changes, `make docs-check`, `make docs-freshness`, and
targeted tests are usually enough.

## Git Safety

Preserve dirty work in sibling repos. Do not archive, rename, or mutate old
remotes unless explicitly asked.
