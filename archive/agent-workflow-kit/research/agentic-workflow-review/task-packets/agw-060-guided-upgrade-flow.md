# AGW-060 Task Packet: Guided Upgrade Flow

## Task

- ID: `AGW-060`
- Title: Expand guided upgrade flow beyond profile-schema migration.
- Priority: `P2`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv:61`
- Repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`

## Context

Future kit updates need a clearer operator path for reviewing conflicts and
applying richer upgrades safely beyond profile-config metadata migration.

Safe-start evidence:

- `make backlog-status` reports `1` open, `100` done, `0` partial, with
  `AGW-060` selected next.
- `make agent-next` selects `AGW-060` and reports `dirty: false`.
- `make agent-task-status` reports zero active tasks and no coordination
  warnings.
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit` is clean at `4c829a3`.
- Prior AGW-059 work is committed in Codex_CodeReview as `109ab88`.

Non-goals:

- Do not add automatic conflict resolution or force-overwrite behavior.
- Do not mutate target-owned files outside existing explicit update commands.
- Do not add hosted update services, PR creation, branch protection changes, or
  external account writes.
- Do not replace update-plan, update, doctor, or migrate-config; make the
  operator path clearer over those commands.

## Scope

Inspect first:

- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/README.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/docs/rollout-guide.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/repo_contract_kit.py`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/scripts/update.py`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/tests/test_repo_contract_kit_cli.py`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/tests/test_update.py`

Allowed edits:

- `README.md`
- `docs/rollout-guide.md`
- `docs/upgrade-flow.md`
- relevant installed templates under `templates/common/**`
- `scripts/repo_contract_kit.py`
- `scripts/update.py`
- focused CLI/update/install tests
- `VERSION`
- `CHANGELOG.md`
- Codex_CodeReview dogfood and backlog closeout files after validation

Protected:

- Destructive git commands, forced cleanups, and automatic conflict acceptance.
- Target-owned files except through existing explicit update/proposal
  mechanisms.
- Hosted PRs, branch protections, issue trackers, labels, queues, or external
  accounts.
- Agent-workflow-kit prompt source in Codex_CodeReview.

## Acceptance Criteria

- Operators have a clear safe upgrade sequence from status through dry-run,
  conflict review, update, doctor, and verification.
- Conflict reports and proposed replacements are explained as review artifacts,
  not auto-apply instructions.
- Existing profile-schema migration remains one step inside the broader upgrade
  flow.
- No destructive update behavior or external hosted mutation is added.

## Validation

Run from `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_repo_contract_kit_cli tests.test_update tests.test_install`
- `PYTHONDONTWRITEBYTECODE=1 make test`
- `make docs-check`
- `make version-check`
- `git diff --check`

Run from `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview` after dogfood update:

- `make kit-update KIT=/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- `make backlog-check && make backlog-split-check && make backlog-status && make agent-next`
- `make kit-status KIT=/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- `make docs-check && make version-check && git diff --check`

Final closeout must prove zero open backlog items remain.

## Documentation Impact

Expected: yes.

Required docs/update paths:

- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/docs/upgrade-flow.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/README.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/docs/rollout-guide.md`
- `/Volumes/Myrtle/Code/04_Code/repo-contract-kit/CHANGELOG.md`
- `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/research/agentic-workflow-review/summary.md`
- `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview/CHANGELOG.md`

No docs waiver is allowed because this task changes operator upgrade guidance.

## Risk And Approval

Risk level: medium.

Known risks:

- Upgrade guidance could imply conflict reports should be auto-applied.
- CLI changes could accidentally change update mutability semantics.
- Docs could duplicate or conflict with update-plan and migrate-config guidance.
- Final closeout must prove no open backlog rows remain rather than assuming
  completion.

Approval: approved by the user's serial backlog execution request.
