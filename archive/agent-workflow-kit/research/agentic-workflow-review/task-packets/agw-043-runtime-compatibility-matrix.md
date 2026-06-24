# AGW-043 Task Packet: Runtime Compatibility Matrix

## Task

- ID: `AGW-043`
- Title: Add compatibility matrix for Codex, Claude Code, Cursor, Continue,
  Copilot, Goose, Aider, Cline/Roo.
- Priority: `P2`
- Repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Status: `approved`
- Source: `research/agentic-workflow-review/backlog.csv:44`

`agent-workflow-kit` records current Codex and GitHub Copilot projections plus
planned runtime adapters, but operators do not have one current matrix that
explains which artifact each major coding-agent runtime consumes, what this kit
supports now, what remains planned, and when manual prompt use is safer than
generating another adapter.

## Safe Start Evidence

- Source `main` is clean and pushed at
  `5a87434198b0f0a061c3a70b56478ddbf2bcebb0`.
- `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1
  TASK_STATUS_JSON=1` reports zero active tasks, no stale tasks, no hazards, no
  unknown-scope tasks, and no untracked agent worktrees.
- `make agent-next` selects `AGW-043` with `dirty: false`.
- `make backlog-status` reports `10` open and `89` done.
- `make agent-token-budget` reports 102 files and 83344 estimated tokens,
  result `passed`.
- `make kit-status` reports installed `repo-contract-kit` 0.4.41, target repo
  version 0.2.20, runtime adapters `none`, and managed-file drift relative to
  installed kit metadata. Treat that as known self-dogfood drift, not source git
  dirt.

Decision: `safe-start`.

## Implementation Scope

Allowed edits:

- `docs/runtime-compatibility.md`
- `docs/runtime-adapters.md`
- `docs/agent-workflow-stack.md` if a short cross-link is useful
- `docs/using-the-prompt-kit.md` if a short cross-link is useful
- `README.md`
- `VERSION` and `CHANGELOG.md` if version policy requires a docs patch bump
- source backlog closeout files:
  - `research/agentic-workflow-review/backlog.csv`
  - `research/agentic-workflow-review/agent-workflow-kit-backlog.csv`
  - `research/agentic-workflow-review/summary.md`
  - `research/agentic-workflow-review/feature_matrix.csv`

Protected:

- `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit/`
- `workflows/prompts/`
- `.codex/prompts/`
- `.github/copilot-instructions.md`
- `workflows/manifest.json` unless a documentation-only typo is proven and
  reviewed
- `scripts/`
- `tests/`
- `.agent-workflows/` runtime state except deterministic report reads
- unrelated backlog rows and unrelated dirty work

## Inspect First

Read:

- `AGENTS.md`
- `REVIEW.md`
- `.agent-workflows/README.md`
- `docs/runtime-adapters.md`
- `docs/agent-workflow-stack.md`
- `workflows/manifest.json`
- `README.md`

Run or refresh:

- `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`
- `make kit-status`
- `make stack-status KIT=/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`

Refresh primary runtime docs before writing compatibility claims. At minimum,
check current docs for:

- OpenAI Codex `AGENTS.md`:
  <https://developers.openai.com/codex/guides/agents-md>
- OpenAI Codex skills:
  <https://developers.openai.com/codex/skills>
- Claude Code memory/project instructions:
  <https://code.claude.com/docs/en/memory>
- Cursor rules:
  <https://cursor.com/docs/rules>
- Continue rules:
  <https://docs.continue.dev/customize/rules>
- GitHub Copilot custom instructions:
  <https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions>
- VS Code Copilot custom instructions:
  <https://code.visualstudio.com/docs/agent-customization/custom-instructions>
- Goose hints and persistent instructions:
  <https://goose-docs.ai/docs/guides/context-engineering/using-goosehints/>
  and
  <https://goose-docs.ai/docs/guides/context-engineering/using-persistent-instructions/>
- Aider conventions:
  <https://aider.chat/docs/usage/conventions.html>
- Cline rules:
  <https://docs.cline.bot/customization/cline-rules>
- Roo Code custom instructions:
  <https://roocodeinc.github.io/Roo-Code/features/custom-instructions/>

If a source has moved, use the current canonical URL and record the access date
in the new doc.

## Expected Shape

Add `docs/runtime-compatibility.md` with:

- a clear owner note: `agent-workflow-kit` owns compatibility docs and prompt
  source; `repo-contract-kit` owns target-repo install/update writes; target
  repos own day-to-day runtime state.
- a matrix covering Codex, Claude Code, Cursor, Continue, GitHub Copilot,
  Goose, Aider, Cline, and Roo Code.
- columns or equivalent fields for:
  - runtime
  - native artifact or instruction surface
  - current `agent-workflow-kit` artifact
  - generated today, planned, manual-only, or unsupported/unknown status
  - whether `repo-contract-kit` installs it today
  - source of truth
  - validation source URL and access date
  - limitations
  - privacy/locality notes
- a short section explaining current support:
  - Codex prompts are generated under `.codex/prompts/`.
  - GitHub Copilot repository instructions are generated under
    `.github/copilot-instructions.md`.
  - Codex skill-pack exports are generated on demand under
    `dist/codex-skill-pack/`.
  - Claude, Cursor, Continue, Windsurf, and plain outputs remain planned in
    `workflows/manifest.json`.
  - Goose, Aider, Cline, and Roo Code are manual or compatibility-note surfaces
    unless a future backlog item adds a real adapter.
- guidance for when not to generate an adapter:
  - the runtime already reads `AGENTS.md` or another shared instruction surface;
  - the format is unstable or not documented by a primary source;
  - the adapter would duplicate a prompt without preserving required closeout,
    receipt, privacy, or task-packet evidence;
  - private/user context would be copied into a hosted runtime without review;
  - no validation command or owner exists for keeping it current.

Update nearby docs with short discoverability links. Do not duplicate the full
matrix in `README.md` or `docs/runtime-adapters.md`.

## Non-Goals

- No new runtime adapter generation.
- No repo-contract-kit installer, update, managed-file, or runtime adapter
  selection changes.
- No canonical prompt, schema, runner, lifecycle, or generated adapter changes.
- No claims of official support without a current primary-source reference.
- No release tags, PRs, hosted automation, account setup, or tool configuration.

## Acceptance

1. `docs/runtime-compatibility.md` includes Codex, Claude Code, Cursor,
   Continue, GitHub Copilot, Goose, Aider, Cline, and Roo Code.
2. The matrix distinguishes generated today, planned, manual-only, and
   unsupported/unknown states without implying adapter support that does not
   exist.
3. Runtime claims are grounded in current primary sources with URLs and an
   access date, and uncertainty is explicit.
4. The document explains source/install/target ownership.
5. The document includes privacy/locality guidance for private context, hosted
   agents, ignored local files, and manual prompt transfer.
6. `README.md` and nearby runtime docs make the matrix discoverable without
   duplicating it.
7. The change does not modify runtime adapter generation, canonical prompts,
   schema behavior, repo-contract-kit files, or generated adapter outputs.
8. Backlog rows, split backlog, summary, and feature matrix close `AGW-043`
   only after validation passes.

## Required Validation

Run in the source repo:

- `make docs-check`
- `make docs-freshness`
- `make docs-lint`
- `make docs-build`
- `make docs-generate`
- `python3 scripts/check_doc_impact.py`
- `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
- `PYTHONDONTWRITEBYTECODE=1 make validate`
- `make version-check`
- `make backlog-check`
- `make backlog-split-check`
- `git diff --check`

For `make version-check`, either update `VERSION` and `CHANGELOG.md` if the
docs policy treats the new compatibility guide as release-visible, or record a
specific `VERSION_CHECK_ALLOW_UNCHANGED=1` docs-only rationale if the local
policy accepts no release impact.

Capture:

- runtime documentation URLs checked and their access date
- `git diff --name-only` showing docs/backlog/version scope only
- validation command outputs and any pre-existing warnings by file and line
- version/changelog decision and rationale
- final `git status` and `make agent-task-status` output

## Closeout

- Commit and push source `main`.
- Record or link a final receipt at
  `.agent-workflows/tasks/agw-043-runtime-compatibility-matrix/receipt.json` or
  a durable sidecar equivalent.
- Run or record why unavailable:
  `make agent-task-ready TASK=AGW-043 TASK_READY_JSON=1`.
- Finish any local task metadata with:
  `make agent-task-finalize TASK=AGW-043 TASK_RECEIPT=<path>
  TASK_FINALIZE_JSON=1` or record why unavailable for this parent-run packet.
- Run:
  `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1`.
- Preview closeout cleanup if available:
  `make agent-task-closeout TASK=AGW-043 TASK_CLOSEOUT_JSON=1`.
- Final handoff must say whether the source checkout is clean, only expected
  files remain dirty, cleanup is blocked, or unrelated dirt was preserved.
