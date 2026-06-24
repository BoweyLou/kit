# AGENTS.md

## Purpose

This repository uses docs-as-code. Documentation is part of the definition of done.

If you change code, you must consider whether documentation also needs to change.

## Agent self-start

If asked to review, understand, clean up, or formalize this repo, start here:

1. Read `AGENTS.md`, `REVIEW.md`, and `.agent-workflows/README.md`.
2. Run `make agent-start` to create a local startup packet under
   `.agent-workflows/runs/`.
3. Inspect `make kit-status` and `make version-status` output when available so
   you know the installed kit version, vendored prompt snapshot, and target repo
   version.
4. Inspect `docs/ops/agent-tool-network-allowlist.md` and the selected trust
   profile in `.agent-workflows/agent-permission-policy.json` before running
   review agents, browser research, or CI adapters.
5. Inspect `docs/ops/agent-instruction-hygiene.md` before adding new
   agent-facing rules so `AGENTS.md` stays an index instead of a context dump.
6. Follow `.agent-workflows/repo-review.md` in the requested mode. Use
   `bootstrap` for the first review of an inherited or newly instrumented repo.
7. Use the installed personas and prompts under `.codex/prompts/` where useful.
8. Run `make agent-verify` and `make agent-docs-localize` before proposing code
   changes.
9. Produce a findings backlog before editing code.
10. If work starts from a backlog item, issue, accepted finding, or broad human
   request, run `make agent-task-packet` and convert one selected item into
   scoped executable work before implementation.
11. Before launching or handing off write-capable parallel work, run
   `make agent-task-status` so active task scopes and sibling worktrees are
   visible.

This checkout is legacy `agent-workflow-kit` history. New workflow-source work
belongs in the companion `repo-contract-kit` repo's `workflows` directory, not
in `workflows/prompts/` here. Local `workflows/prompts/` and `.codex/prompts/`
are archive and migration mirrors; if an explicit archive task edits them, run
`make prompt-adapters-export` and `make validate`.

## Self-dogfood boundary

This repo uses `repo-contract-kit` to organize itself, but installed guardrails
must not redefine archive evidence as live source. In this checkout, edit
`workflows/prompts/`, schemas, scripts, or research/backlog files only for
archive validation, migration evidence, or cleanup. Guardrail work belongs in
`AGENTS.md`, `REVIEW.md`, `doc-contract.json`, `.agent-workflows/`, or docs/ops.

Run `make self-check` before and after kit maintenance to verify the legacy
prompt mirror, adapter sync, localizations, and explicit updates.

## Where documentation lives

- `README.md` — high-level overview and getting started
- `docs/working-rhythm.md` — human-facing operator rhythm and mental model
- `docs/` — project documentation
- `docs/adr/` — architecture decision records
- `doc-contract.json` — repository-specific documentation impact rules
- `.github/pull_request_template.md` — PR checklist and change classification

## Documentation contract

If you change any of the following, update the relevant docs in the same change:

- public behavior
- API
- CLI commands or flags
- config or environment variables
- schema or data contracts
- deployment or operations workflow
- architecture or major design decisions

If no documentation update is needed, explicitly say why in the PR summary.
Use the exact marker `No docs needed: <reason>`.

## Versioning contract

If this repo has `VERSION`, `CHANGELOG.md`, and `docs/versioning.md`, treat
`VERSION` as the local SemVer source of truth. Run `make version-check` when a
change affects behavior, APIs, CLI, configuration, schemas, operations, or
user-visible output. Use `make version-bump BUMP=patch|minor|major` only when a
version bump is part of the accepted change scope, then replace the changelog
TODO with a useful summary.

`VERSION` and `CHANGELOG.md` are target-owned files. Do not overwrite them from
kit templates during updates.

## Kit updates

For kit setup/status/update/doctor requests, check `command -v kit` and run the
requested `kit` subcommand from the target repo; do not search for `kit-setup`.
Use `make kit-status` to inspect the installed kit version, source ref, recorded
prompt snapshot, profiles, manifest status, managed-file cleanliness, and target
repo version. Use
`make kit-status KIT=/path/to/repo-contract-kit` when a local kit checkout is
available and you need a `current`/`available` update signal. Use
`make kit-update KIT=/path/to/repo-contract-kit` only when the user asks to
refresh the local kit guardrail files from that checkout, or
`make kit-refresh KIT=/path/to/repo-contract-kit` when the user wants to pull a
clean local kit checkout first and then update. Do not use kit updates to
refresh live workflow source from this checkout; live source lives in
`repo-contract-kit`'s `workflows` directory. If archive work edits
`workflows/prompts/`, regenerate adapters explicitly. Customized managed files
must be preserved; review proposals under `.doc-contract-kit/updates/`.
Use `make kit-update-stack` from a target repo when the same operation should
also update this source repo's dogfood install; pass `KIT=...` or `WORKFLOW=...`
only when discovery needs an override. Use `make kit-refresh-stack` when the
local kit checkout should be cleanly fast-forwarded first.

Use the review-risk tier from `make agent-start` to choose the smallest safe
reviewer set. High-risk or critical changes should stay read-only until a human
accepts a scoped implementation task.

## Instruction hygiene

Keep `AGENTS.md` as a short route map. Put detailed rules in scoped contracts,
runbooks, ADRs, or checker config. `make agent-docs-lint` reads
`.agent-workflows/instruction-budgets.json` and warns when agent instruction
files become too large or too rule-heavy.

## ADR rules

Create or update an ADR when the change affects:

- architecture
- major dependencies
- service boundaries
- data flow or storage strategy
- security/privacy tradeoffs
- deployment/runtime model

Do not create ADRs for small bug fixes or routine internal refactors.

## Commands

Before finishing work, run:

- `make docs-lint`
- `make docs-build`
- `make docs-generate`
- `python3 scripts/check_doc_impact.py`
- `make version-check` when behavior or release impact changed

If these fail, fix the issue before considering the task complete.

## Pull request expectations

Every PR must clearly state:

1. what changed
2. whether docs were updated
3. whether an ADR was added or updated
4. if no docs changed, why not

## Important rule

Never leave generated docs stale.
Never change externally visible behavior without considering documentation impact.
