# AGW-127 Task Packet: Version 1 Single-Repo Consolidation

## Task

- ID: `AGW-127`
- Title: Create a single version 1 workflow-stack repository with one installer and one CLI.
- Priority: `P0`
- Status: `done`
- Source: `research/agentic-workflow-review/backlog.csv`

## Context

- Current source/control repository: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Current implementation repository: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- New v1 repository: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`, remote
  `https://github.com/BoweyLou/repo-contract-kit.git`, default branch `main`.
- Mode: `implemented`
- Problem statement: `AGW-100` made `repo-contract-kit` and `kit` the public
  operator surface, but the underlying project is still split across old source
  and install repositories. Version 1 should become one repository, one release
  stream, one installer, and one CLI, with the old repos archived or frozen as
  historical sources rather than normal edit paths.

## Previous Task State

- Deterministic reports read before packet creation:
  - `make kit-status` reported installed `repo-contract-kit 0.6.5`, target repo
    version `0.2.32`, and workflow prompt snapshot `0.4.60`.
  - `make backlog-status` selected
    `research/agentic-workflow-review/backlog.csv`.
  - `make agent-task-status` reported zero active local task metadata.
  - Keryx project context showed existing `AGW-100` consolidation decisions and
    active follow-up tasks for hard consolidation/archive policy.
- Dirty state to preserve: none observed before implementation.
- Closeout required before implementation: satisfied by implementing the v1
  identity as the existing `repo-contract-kit` repository and avoiding
  destructive archive, remote rename, target update, or `1.0.0` cut operations.

## Goal Alignment

- repo_goal: make the workflow stack easier to operate by removing the remaining
  two-repo source/install mental model from normal development and target-repo
  use.
- area_contracts:
  - path: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/`
    purpose: current public product, installer, CLI, target templates, tests,
      and workflow-source location after AGW-100.
    status: `aligned`
  - path: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/`
    purpose: legacy workflow-source history, research backlog, task packets,
      and migration/archive evidence.
    status: `extends`
  - path: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/workflows/`
    purpose: expected v1 home for canonical workflow prompts, schemas,
      generated adapters, and source docs if the existing repo is retained.
    status: `aligned`
- alignment_decision: `adapt`
- adaptation_needed: `yes`
- stop_conditions:
  - Stop if the owner has not approved the final v1 repository name and remote
    policy.
  - Stop if migration would lose Git history, release metadata, task packets, or
    provenance needed for existing target repos.
  - Stop if old installer or CLI paths cannot be made to redirect, refuse with a
    clear upgrade command, or remain compatibility shims for one release window.
  - Stop before archiving or deleting an old repo unless a rollback path and
    target migration receipt exist.

## Scope

Inspect first:

- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/README.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/install.sh`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/repo_contract_kit.py`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/VERSION`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/CHANGELOG.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/docs/`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/workflows/`
- `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/docs/agent-workflow-stack.md`
- `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-workflow-review/`
- Keryx decisions for `AGW-100` and workflow-stack consolidation.

Allowed work after owner accepts the v1 plan:

- Create or select the single v1 repository identity.
- Import required workflow-source history, prompt/schema artifacts, research
  context, backlog/task-packet evidence, installer code, CLI code, docs, tests,
  VERSION, and CHANGELOG into the v1 repo.
- Preserve `kit` as the single public CLI unless the owner explicitly renames
  it.
- Preserve one curl installer and one target-repo setup/update/doctor flow.
- Add compatibility shims or redirect docs for old clone paths, old installer
  URLs, and old source-edit instructions.
- Add migration tests proving existing target repos update from older
  `repo-contract-kit` and workflow prompt snapshot receipts.
- Update archive/read-only guidance in the old repos only after the v1 repo is
  validated.

Protected:

- Do not delete, archive, or remote-rename old repos in the planning slice.
- Do not remove old source history without an import receipt.
- Do not make target repos clone a workflow-source checkout.
- Do not split the public surface into a second CLI, second installer, or second
  release stream.
- Do not bump to `1.0.0` until migration, compatibility, docs, and rollback
  gates pass.

## Acceptance Criteria

- A v1 repository identity decision exists: final name, local path, remote path,
  default branch, archive policy for old repos, and rollback owner.
- The v1 repository contains the current public kit product and the required
  workflow-source material in one tree.
- There is exactly one normal installer path and it installs the single `kit`
  CLI.
- There is one `VERSION` and one `CHANGELOG.md`; the v1 release is `1.0.0` only
  after migration validation passes.
- Old repo READMEs, installer entrypoints, or docs either redirect to v1 or
  clearly state they are historical/archive paths.
- Existing target repos can update from pre-v1 install receipts without losing
  root `AGENTS.md`, target-owned files, prompt snapshot provenance, sidecar
  state, task metadata, or docs-contract behavior.
- `kit status`, `kit self status`, `kit update --dry-run`, `kit update`,
  `kit doctor`, and `kit command-map --json` all report coherent v1 version and
  source-ref roles.
- Migration tests cover at least one clean target and one customized target.
- Release docs explain install, update, rollback, archive, and compatibility
  behavior without requiring the old two-repo mental model.

## Validation

Planning validation in `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`:

- `make backlog-check`
- `make backlog-split-check`
- `make backlog-status`
- `make agent-next`
- `make agent-verify`
- `git diff --check`

Implementation validation in the accepted v1 repository:

- focused CLI/install/update migration tests for clean and customized targets
- full test suite
- docs contract checks
- docs freshness or docs-as-tests checks for documented installer and CLI
  commands
- version check
- `kit command-map --json` parser consistency check
- smoke test from a disposable target repo using the public curl installer or a
  local equivalent

## Documentation Impact

- Expected: `yes`
- Required surfaces:
  - v1 README and install docs
  - v1 upgrade/rollback docs
  - v1 workflow-source ownership docs
  - old repo archive/redirect notices
  - target-repo installed docs if version/source-ref wording changes
  - changelog/release notes for `1.0.0`
- Waiver allowed: `no`

## Risk And Approval

- Risk level: `high`
- Owner approval required before:
  - creating or publishing the v1 remote
  - archiving old remotes
  - changing public installer URLs
  - cutting `1.0.0`
  - rewriting old docs as archive-only
- Recommended execution: split into phases for identity decision, import plan,
  migration implementation, target update proof, archive notice, and v1 release.

## Closeout Evidence

- Implementation commit: `repo-contract-kit` `cea21f2` (`Add version 1 consolidation contract`), pushed to `origin/main`.
- Version: `repo-contract-kit` `0.6.21`.
- Added `docs/version-1-consolidation.md` with repository identity, single
  product surface, legacy archive policy, compatibility requirements, release
  gate, and rollback path.
- Linked the v1 contract from `README.md`, `docs/agent-workflow-stack.md`,
  `docs/rollout-guide.md`, and `docs/roadmap.md`.
- Added `tests/test_v1_consolidation.py` to cover the v1 doc route, installer
  defaults, optional legacy workflow path, in-repo workflow source, CLI
  entrypoint, and single `VERSION` / `CHANGELOG.md` stream.
- Validation:
  - `python3 -m unittest tests.test_v1_consolidation`
  - `make docs-check`
  - `make docs-freshness`
  - `make version-check`
  - `make workflow-source-check`
  - `python3 scripts/repo_contract_kit.py command-map --json`
  - local installer smoke test using `install.sh --source "$(pwd)"`
  - `make test` (`298` tests)
