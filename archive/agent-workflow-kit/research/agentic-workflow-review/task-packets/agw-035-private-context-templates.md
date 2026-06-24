# AGW-035 Task Packet: Private Context Templates

## Task

- ID: `AGW-035`
- Title: Add optional project/user/private context templates with privacy warnings.
- Priority: `P2`
- Repo: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- Status: approved
- Source: `research/agentic-workflow-review/backlog.csv:36`

Some target repos need a place to record project preferences, user preferences,
and private local context for agents, but repo-contract-kit must make the safe
path explicit so secrets and personal context are not accidentally committed or
copied into hosted prompts.

## Safe Start Evidence

- Source `main` is clean and pushed at
  `2828d372d2a1706242855c8f7fc0df47d31913a3`.
- Repo-contract-kit `main` is clean and pushed at
  `c12c19c3d0fe2b5744c22b07a371a1e8728b4674`.
- Source `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1
  TASK_STATUS_JSON=1` reports zero active tasks, no stale tasks, and no hazards.
- Source `make backlog-status` reports `11` open and `88` done.
- Source `make agent-next` selects AGW-035 with `dirty: false`.
- `make agent-task-packet-from-backlog BACKLOG_ID=AGW-035` confirms the
  delivery shape is `Templates and gitignore guidance.`

Decision: safe-start.

## Implementation Scope

Allowed kit areas include:

- `templates/profiles/private-context/`
- `templates/common/ops-agent-workflow.md`
- `templates/common/working-rhythm.md`
- `templates/common/agent-tool-network-allowlist.md`
- `README.md`
- `docs/rollout-guide.md`
- `docs/roadmap.md`
- `docs/harness-engineering.md`
- focused installer/update/CLI tests such as `tests/test_install.py`,
  `tests/test_update.py`, and `tests/test_repo_contract_kit_cli.py`
- `VERSION`
- `CHANGELOG.md`

Source closeout is limited to:

- `research/agentic-workflow-review/backlog.csv`
- `research/agentic-workflow-review/repo-contract-kit-backlog.csv`
- `research/agentic-workflow-review/summary.md`
- `research/agentic-workflow-review/feature_matrix.csv`

Protected:

- agent-workflow-kit canonical prompts, schemas, generated adapters, and
  runtime adapter source files
- repo-contract-kit review runner, task runner, context bundle, preflight,
  self-heal, and lifecycle behavior
- existing preset membership except tests proving the new profile is absent
  from presets
- target-owned `VERSION` and `CHANGELOG.md` in installed target repos
- real private context files without `.example` or equivalent safe naming
- unrelated backlog rows and unrelated dirty work

## Expected Shape

Preferred shape:

- Add a new explicit optional profile, likely `private-context`, installable
  with:

  ```bash
  python3 scripts/install.py /path/to/repo --profile private-context
  ```

- Keep `private-context` out of `minimal`, `learning`, `test-first`, and
  `agentic` presets.
- Install managed example templates for:
  - shareable project context
  - user preference context
  - private local context
- Install a managed context directory `.gitignore` that tracks README/example
  guidance but ignores real local context files by default.
- Make the examples explicit that they are not secret stores and must not
  contain tokens, cookies, passwords, private URLs, account identifiers,
  customer data, medical/financial data, personal messages, or proprietary
  snippets that should not leave the machine.
- Explain how to review/redact context before sharing with hosted models,
  browser tools, GitHub comments, PRs, issues, or external tickets.
- Explain the difference between:
  - `AGENTS.md` and `REVIEW.md` as durable shared repo instructions
  - runtime adapters such as `CLAUDE.md`
  - optional private-context files
  - Keryx/Obsidian or other external memory systems
  - secrets management
- Add installer tests for explicit profile install, composed profile install,
  preset absence, manifest entries, and gitignore behavior.
- Bump repo-contract-kit patch version and changelog.
- Close source backlog rows only after the kit implementation is validated and
  pushed.

## Non-Goals

- No default or `agentic` preset inclusion.
- No real private context, secrets, credentials, private URLs, customer data,
  personal messages, account identifiers, or machine-specific paths.
- No memory system, Keryx/Obsidian integration, browser profile integration,
  hosted sync, secret scanner, or external planning adapter.
- No agent-workflow-kit prompt/source changes.
- No runner, context-bundle, lifecycle, self-heal, or preflight behavior change.
- No lint/docs/token-budget behavior that reads ignored private context files by
  default.

## Acceptance

1. The optional `private-context` profile installs explicitly and is absent from
   all existing presets.
2. Installed profile files provide project, user, and private context examples
   with clear privacy warnings and no live-looking secret or personal data
   placeholders.
3. The installed context directory tracks only README/example guidance and
   ignores real local context files by default.
4. Docs explain safe use, review/redaction before sharing, and why the profile
   is opt-in.
5. Update behavior remains safe: managed template changes are tracked in the
   manifest and customized managed files are not overwritten silently.
6. The change does not add memory integrations, prompt-source changes, runtime
   adapter changes, or runner behavior.
7. repo-contract-kit version/changelog records the new opt-in profile, and
   source backlog closeout records AGW-035 only after kit validation and push.

## Required Validation

Run in repo-contract-kit:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install tests.test_update tests.test_repo_contract_kit_cli`
- `PYTHONDONTWRITEBYTECODE=1 make test`
- `make docs-check`
- `make docs-freshness`
- `make version-check`
- `git diff --check`
- Install smoke: install `--profile private-context` into a temporary git repo,
  verify example files and `.gitignore` behavior, then verify real private
  context files are ignored.

Run in the source repo after kit validation and source closeout:

- `make backlog-check`
- `make backlog-split-check`
- `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
- `git diff --check`

## Closeout

- Commit and push the repo-contract-kit implementation first.
- Then close AGW-035 in source backlog files and push source `main`.
- Record or link a final receipt at
  `.agent-workflows/tasks/agw-035-private-context-templates/receipt.json` or a
  durable sidecar equivalent.
- Run or record why unavailable:
  `make agent-task-ready TASK=AGW-035 TASK_READY_JSON=1`.
- Finish any local task metadata with:
  `make agent-task-finalize TASK=AGW-035 TASK_RECEIPT=<path> TASK_FINALIZE_JSON=1`
  or the local lifecycle fallback.
- Final handoff must say whether both repos are clean, only expected files
  remain dirty, cleanup is blocked, or unrelated dirt was preserved.
