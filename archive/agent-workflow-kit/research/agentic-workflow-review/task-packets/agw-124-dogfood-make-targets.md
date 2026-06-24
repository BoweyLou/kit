# AGW-124 Task Packet: Dogfood Make Targets

## Source

- Backlog item: `AGW-124`
- Source repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Status: `done`

## Problem

The operator docs advertise installed kit targets such as `make goal-check`,
`make agent-context-bundle`, `make agent-state-ledger`,
`make agent-preflight`, `make docs-as-tests`, and `make agent-task-ready`.
This legacy dogfood checkout owns its root `Makefile` directly, so those
documented commands failed locally when the root file did not mirror the
installed target surface.

## Scope

- Add explicit root `Makefile` wrappers for documented installed-kit commands
  used by the active operator docs.
- Keep the root `Makefile` target-owned; do not include the managed fragment
  wholesale.
- Document the dogfood strategy in `docs/ops/agent-workflow.md`.
- Mark that runbook localization intentional in the self-dogfood boundary
  checker, ADR, and tests.
- Add regression coverage that checks active operator docs against root
  `Makefile` targets, not only against the managed kit fragment.

## Non-Goals

- Do not change the canonical installed target definitions in
  `repo-contract-kit`.
- Do not run a kit update or rewrite kit-managed files from templates.
- Do not change the behavior of the underlying CLI or task lifecycle scripts.

## Validation

- `python3 -m unittest tests.test_documented_make_targets`
- `make -n goal-check agent-context-bundle agent-state-ledger agent-branch-readiness agent-preflight agent-self-heal docs-as-tests agent-instruction-diet agent-docs-explain agent-docs-propose agent-changelog-update agent-task-ready agent-task-finalize agent-automation-handoff kit-migrate-config TASK=AGW-124 KIT=/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- `make docs-freshness`
- `make docs-check`
- `make agent-docs-lint`
- `make agent-verify`
- `git diff --check`

## Closeout Evidence

- Root `Makefile` now exposes the documented wrappers for goal checks, compact
  context, state ledger, branch readiness, preflight/doctor, self-heal,
  docs-as-tests, instruction diet, docs explain/propose, changelog proposal,
  task readiness/finalization, automation handoff, and kit config migration.
- `tests/test_documented_make_targets.py` fails if active operator docs mention
  a `make <target>` command missing from this checkout's root `Makefile`.
- `docs/ops/agent-workflow.md` now states that this legacy dogfood checkout
  keeps explicit target-owned wrappers for documented local commands.
- The self-dogfood boundary now treats that local runbook note as an intentional
  managed-file localization rather than unexplained kit drift.
