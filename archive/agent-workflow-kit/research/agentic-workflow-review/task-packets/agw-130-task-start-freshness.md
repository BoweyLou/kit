# AGW-130 Task Packet: Task-Start Freshness

## Source

- Backlog item: `AGW-130`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Implementation commit: `33e6a4d`
- Released version: `repo-contract-kit` `0.6.22`
- Status: `done`

## Problem

Task startup needed to make global-tool and target-install drift visible before
write-capable work starts, without turning every normal task into an automatic
tooling migration.

## Scope

- Extend `make agent-start` / `scripts/agent_start.py` to emit a read-only
  `task_start_freshness` section in the startup packet and agent brief.
- Reuse existing `kit_drift` diagnostics so startup reports global kit metadata,
  target install metadata, repo cleanliness, backlog source, and safe update
  modes.
- Define report-only, dry-run, auto-update-clean, and maintenance policies while
  keeping startup non-mutating.
- Document the startup freshness section in repo-contract-kit README,
  `docs/harness-engineering.md`, and the installed operator workflow template.
- Cover stale target install behavior with tests.

## Non-Goals

- Do not make `agent-start` apply `kit update`, `kit update --global`, or
  target setup automatically.
- Do not change the existing status/doctor `kit_drift` classification contract.
- Do not require every task start to run a target update dry-run.

## Validation

- `python3 -m unittest tests.test_agent_start`
- `python3 -m unittest tests.test_agent_start tests.test_repo_contract_kit_cli`
- `make docs-check`
- `make docs-freshness`
- `make version-check`
- `make workflow-source-check`
- `make test`
- `git diff --check`

## Closeout Evidence

- `repo-contract-kit` commit `33e6a4d` adds `task_start_freshness` to
  `agent-start` packets and briefs.
- The default selected policy is `report-only`, and the packet records
  `auto_apply_performed=false` with no target or sidecar writes for freshness
  diagnostics.
- Stale target installs recommend `dry-run` and expose a gated
  `auto-update-clean` mode only when the checkout is clean and explicit approval
  is supplied outside startup.
- Full repo-contract-kit validation passed with `299` tests.
