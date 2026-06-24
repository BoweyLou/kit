# AGW-059 Task Packet: Planning And Memory Adapter Examples

## Task

- ID: `AGW-059`
- Title: Add external planning and memory adapter examples for task-packet handoffs.
- Priority: `P2`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv:60`
- Repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`

## Context

Target repos need examples for linking backlog mirrors to Keryx, Obsidian,
issues, or other planning systems without turning repo-contract-kit into a
planning application.

Safe-start evidence:

- `make backlog-status` reports `2` open, `99` done, `0` partial, with
  `AGW-059` selected next.
- `make agent-next` selects `AGW-059` and reports `dirty: false`.
- `make agent-task-status` reports zero active tasks and no coordination
  warnings.
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit` is clean at `d4a22f0`.
- Prior AGW-058 work is committed in Codex_CodeReview as `31859f1`.

Non-goals:

- Do not add Keryx, Obsidian, GitHub Issues, Linear, Jira, or hosted planning
  API clients.
- Do not make repo-contract-kit the source of priority truth for target repos.
- Do not write to external memory systems, vault files, issues, pull requests,
  labels, or project boards.
- Do not change task-packet schema semantics unless examples expose a strictly
  necessary documentation-only clarification.

## Goal Alignment

- Repo goal: repo-contract-kit installs local-first docs-as-code and agent
  workflow guardrails while preserving target-owned planning decisions.
- Aligned areas:
  - `docs/` for maintainer and operator planning handoff examples.
  - `templates/common/` or `templates/profiles/local-agentic/` only if the
    examples should install into target repos.
  - `tests/` only if installed docs/templates or freshness checks need coverage.
- Decision: `aligned`.
- Stop if the work becomes a writable Keryx, Obsidian, GitHub, Linear, or Jira
  integration.

## Scope

Inspect first:

- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/README.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/docs/rollout-guide.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/docs/roadmap.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/docs/harness-engineering.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/common/ops-agent-workflow.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/templates/profiles/local-agentic/files/.agent-workflows/README.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/agent_start.py`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/repo_contract_kit.py`

Allowed edits:

- `README.md`
- `docs/rollout-guide.md`
- `docs/roadmap.md`
- `docs/harness-engineering.md`
- `docs/planning-adapters.md`
- relevant installed templates under `templates/common/**` or
  `templates/profiles/local-agentic/**`
- focused tests if installed docs/templates change
- `VERSION`
- `CHANGELOG.md`
- Codex_CodeReview dogfood and backlog closeout files after validation

Protected:

- External Keryx, Obsidian, GitHub, Linear, Jira, or planning-system state.
- Credentials, tokens, browser sessions, vault files, issues, PRs, labels, and
  project boards.
- Task-packet schema behavior unless a documentation-only clarification is
  necessary.
- Agent-workflow-kit prompt source in Codex_CodeReview.

## Acceptance Criteria

- Examples show how external planning or memory systems hand off one selected
  item into a task packet without becoming repo-contract-kit state.
- Keryx, Obsidian, issues, and `docs/backlog.md` mirror patterns are described
  as examples, not built-in adapters.
- Installed target guidance is updated where useful and remains local-first.
- Operator docs explain what to do when external planning state and repo backlog
  mirrors disagree.

## Validation

Run from `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install tests.test_check_docs_freshness`
- `PYTHONDONTWRITEBYTECODE=1 make test`
- `make docs-check`
- `make version-check`
- `git diff --check`

Run from `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview` after dogfood update:

- `make kit-update KIT=/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- `make backlog-check && make backlog-split-check && make backlog-status && make agent-next`
- `make kit-status KIT=/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- `make docs-check && make version-check && git diff --check`

Capture evidence:

- Planning adapter docs/template diffs.
- Focused and full repo-contract-kit validation output.
- Evidence that no external writes/API clients were added.
- Dogfood `kit-status` output.
- Backlog closeout status and next open item.

## Documentation Impact

Expected: yes.

Required docs/update paths:

- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/docs/planning-adapters.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/README.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/docs/rollout-guide.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/CHANGELOG.md`
- `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-workflow-review/summary.md`
- `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/CHANGELOG.md`

No docs waiver is allowed because this task is explicitly about docs/examples.

## Risk And Approval

Risk level: medium.

Known risks:

- Examples could be mistaken for supported writable adapters.
- Backlog mirrors could be treated as priority truth instead of reviewed copies
  from an external planner.
- External memory examples could encourage unsafe vault or issue tracker writes.
- Installed docs could duplicate or conflict with existing backlog command
  guidance.

Approval: approved by the user's serial backlog execution request.

Recommended prompt: `workflows/prompts/fix-implementer.md`.

Next packet hint: keep guided upgrade-flow work separate for `AGW-060`.
