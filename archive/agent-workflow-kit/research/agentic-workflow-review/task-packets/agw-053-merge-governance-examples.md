# AGW-053 Task Packet: Merge Governance Examples

## Task

- ID: `AGW-053`
- Title: Add merge-governance examples for GitHub branch protection and merge
  queues that consume repo-contract-kit readiness signals.
- Priority: `P2`
- Repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv:54`

## Context

`AGW-052` is complete: repo-contract-kit has `branch-readiness` /
`make agent-branch-readiness` as a no-write local aggregate for branch/PR
readiness evidence. `AGW-053` should add documentation examples that show how a
repo owner can use that local signal alongside GitHub protected branches, status
checks, and merge queues without making repo-contract-kit mutate GitHub state.

Current safe-start evidence:

- `make backlog-status` reports `5` open, `96` done, and selects `AGW-053`.
- `make agent-next` selects `AGW-053`; the only source-repo dirt before this
  packet commit is the AGW-053 task-packet files themselves.
- `make agent-task-status` reports zero active tasks and no coordination
  warnings.
- `repo-contract-kit` is clean at local commit `76e2129`, version `0.6.1`.
- `AGW-052` validation passed under repo-contract-kit 0.6.0:
  `tests.test_branch_readiness tests.test_repo_contract_kit_cli tests.test_install`,
  full `make test`, `make docs-check`, `make version-check`, and
  `git diff --check`.
- repo-contract-kit 0.6.1 additionally validated the current target-migration
  path from a 0.4.54 dummy repo, including root `AGENTS.md` preservation and
  customized managed-file conflict reporting.

## Scope

Inspect first:

- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/README.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/docs/rollout-guide.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/docs/harness-engineering.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/common/ops-agent-workflow.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/common/working-rhythm.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/common/harness-engineering.md`

Allowed edits:

- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/README.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/docs/`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/common/`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/tests/` if docs freshness or
  install docs tests need updates
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/VERSION`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/CHANGELOG.md`
- Source closeout files under
  `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-workflow-review/`
  after validation

Protected:

- Do not add GitHub API calls, PR comments, status publishing, merge queue
  enqueue/dequeue, branch protection mutation, token handling, or workflow
  secrets.
- Do not change `branch-readiness` behavior unless a docs example exposes a
  proven bug that must be fixed in scope.
- Do not make hosted CI or GitHub required for local readiness.

## Acceptance

- Docs include a concrete owner-operated example for making
  `agent-branch-readiness` a required local evidence step before PR update or
  merge handoff.
- Docs include a GitHub protected-branch/status-check mapping that clearly
  distinguishes repo-contract-kit local evidence from hosted required checks.
- Docs include a merge-queue example that keeps enqueue/dequeue decisions with
  the owner or hosted platform, not repo-contract-kit.
- Examples show required versus advisory checks and how `checks-json` can be
  exported from another tool without network calls by repo-contract-kit.
- Docs explicitly state that repo-contract-kit does not mutate GitHub, branch
  protection, merge queues, labels, PR comments, or credentials.
- `VERSION` and `CHANGELOG.md` record any repo-contract-kit docs/operator
  behavior change if required by repo policy.
- Source backlog rows and summary close `AGW-053` only after repo-contract-kit
  validation passes.

## Validation

Run in `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`:

- `make docs-check`
- `make version-check`
- `PYTHONDONTWRITEBYTECODE=1 make test` if tests or installed templates change
- `git diff --check`

Run in `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview` after source closeout:

- `make backlog-check`
- `make backlog-split-check`
- `make backlog-status`
- `make agent-next`
- `git diff --check`
