# Version 1 Consolidation

This page is the maintainer contract for making the workflow stack one product
before the `1.0.0` release. It turns the post-`AGW-100` direction into an
explicit repository identity, migration proof, archive policy, and rollback
path.

## Repository Identity

The version 1 workflow-stack repository is:

- local path: `/Volumes/Myrtle/Code/04_Code/kit`
- remote: `https://github.com/BoweyLou/kit.git`
- default branch: `main`
- public installer: `https://raw.githubusercontent.com/BoweyLou/kit/main/install.sh`
- public CLI: `kit`

The `kit` repository owns the installer, CLI, target templates, update behavior,
and canonical workflow source under `workflows/`. The older repositories remain
readable only as archive and migration evidence.

## Single Product Surface

Version 1 has one normal operator path:

```bash
curl -fsSL https://raw.githubusercontent.com/BoweyLou/kit/main/install.sh | sh
kit setup
kit status
kit mode-check --json
kit task-packet --harness-mode auto --json
kit verify --harness-mode auto --json
kit update --dry-run
```

Target repos receive generated guardrails and workflow prompt snapshots from
this repository. They must not clone a workflow-source checkout at runtime.
Maintainers may still use `install.sh --with-workflow` only to inspect legacy
`agent-workflow-kit` history during the archive window.

## Legacy Archive Policy

The old `agent-workflow-kit` / `Codex_CodeReview` checkout is legacy source
history. Keep it readable until all required migration evidence has been
carried into this repository.

Archive/freeze rules:

- new prompt, schema, persona, research, task-packet, and installed-template
  source changes start in `kit/workflows/` or the surrounding `kit`
  implementation.
- old-repo changes are limited to archive notices, backlog closeout, migration
  evidence, and compatibility documentation.
- do not delete old Git history.
- do not archive or make the old remote read-only until the latest target
  migration receipt proves clean and customized target updates still work.
- after the archive switch, old README or route-map files should redirect to
  this repository and say the old path is historical.

Archive-switch closeout checklist:

1. Prove a clean target update from the current `kit` checkout.
2. Prove a customized managed-file update produces reviewable proposals under
   `.doc-contract-kit/updates/` instead of overwriting target changes.
3. Record rollback guidance that keeps target-owned files, sidecar state, task
   metadata, and root `AGENTS.md` intact.
4. Update old `Codex_CodeReview` notices and backlog rows so normal source work
   points to `kit`.
5. Keep the old checkout readable for history after the switch.

## Compatibility Requirements

Before cutting `1.0.0`, the repository must prove:

- the default installer provisions only the `kit` checkout and launcher.
- `--with-workflow` remains an opt-in maintainer compatibility path.
- `kit status`, `kit self status`, `kit update --dry-run`, `kit update`,
  `kit doctor`, and `kit command-map --json` report coherent version and source
  roles.
- target update tests cover a clean target and a customized target.
- older install receipts that mention `agent-workflow-kit` migrate to the
  `workflow-source` prompt snapshot name without overwriting root `AGENTS.md`
  or target-owned `VERSION` / `CHANGELOG.md`.
- `make workflow-source-check`, `make test`, `make docs-check`,
  `make docs-freshness`, and `make version-check` pass.

## Version And Release Gate

There is one version stream: root `VERSION` and `CHANGELOG.md` in this
repository. Do not bump to `1.0.0` until the compatibility requirements above
pass and the old-repo archive notice has been updated or deliberately deferred
with a release-note reason.

Patch and minor releases may continue while closing the remaining pre-1.0
backlog. Those releases must keep the single product surface intact.

## Rollback

The rollback owner is the repository maintainer cutting the release.

Rollback path:

1. Stop target updates by leaving target repos on their current installed
   receipt; target updates are explicit and per-repo.
2. Reinstall the previous global tool ref with `kit update --global --ref <tag>`
   or rerun `install.sh --ref <tag>`.
3. For an affected target repo, review `.doc-contract-kit/updates/<timestamp>/`
   and revert only the managed-file update commit that introduced the problem.
4. Keep target-owned files, sidecar state, task metadata, and root `AGENTS.md`
   intact.
5. Record the rollback in `CHANGELOG.md` and leave the old source checkout
   readable until the replacement release is validated.
