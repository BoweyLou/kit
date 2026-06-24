# AGW-031 Task Packet: Advisory Comment/Docstring Drift

## Task

- ID: `AGW-031`
- Title: Add advisory code-comment/docstring drift prompt and false-positive labels.
- Priority: `P2`
- Repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Status: approved
- Source: `research/agentic-workflow-review/backlog.csv:32`

Inline comments and docstrings can become stale in the same way as docs, but
this task should keep the signal advisory and evidence-backed. It should add
prompt/output-label support for comment and docstring drift without creating a
blocking CI gate, static scanner, or automatic source-comment editor.

## Safe Start Evidence

- Source `main` is clean at
  `d594e7028ec1dc69cf645b2437d5bbea129671d1`.
- Repo-contract-kit `main` is clean at
  `c12c19c3d0fe2b5744c22b07a371a1e8728b4674`.
- `make agent-task-status TASK_STATUS_JSON=1` reports zero active tasks, no
  stale tasks, and no hazards.
- `make agent-next` selects AGW-031 with a clean checkout.

Decision: safe-start.

## Implementation Scope

Allowed source areas include:

- `workflows/prompts/personas/doc-code-delta.md`
- `.codex/prompts/personas/doc-code-delta.md`
- `workflows/prompts/templates/review-finding.md`
- `.codex/prompts/templates/review-finding.md`
- `workflows/prompts/review-synthesis.md`
- `.codex/prompts/review-synthesis.md`
- `workflows/prompts/README.md`
- `README.md`
- `docs/using-the-prompt-kit.md`
- `docs/harness-engineering.md`
- `schemas/review-synthesis.schema.json`
- `research/prompt-regression-fixtures/`
- `scripts/run_prompt_regression_fixtures.py`
- `tests/test_prompt_regression_fixtures.py`
- backlog, split backlog, summary, feature matrix, `VERSION`, and
  `CHANGELOG.md` for closeout/bookkeeping

Protected:

- `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- repo-contract-kit managed templates and installed target-repo files
- learning-comments receipt validation unless a direct adapter validation
  issue requires a narrow fix
- runtime review-runner behavior unless fixture validation needs a narrow
  additive label check
- unrelated personas, unrelated backlog rows, and unrelated dirty work

## Expected Shape

Preferred shape:

- Extend `doc-code-delta` so it explicitly reviews behavior-describing
  comments and docstrings for drift.
- Require two-sided evidence: the maintained comment/docstring plus current
  implementation, tests, docs, ADRs, or runtime behavior that contradicts it.
- Keep comment/docstring drift advisory by default. Raise severity only when
  the stale comment/docstring is user-facing, operationally important,
  security/privacy-sensitive, or likely to cause a wrong code change.
- Add output labels or prompt fields for:
  - `comment-drift`
  - `docstring-drift`
  - `stale-comment`
  - `misleading-comment`
  - `stale-docstring`
  - `intentionally-stable-comment`
  - `generated-or-vendored-comment`
  - `low-confidence-drift`
- Add false-positive guidance for generated/vendor files, intentionally
  historical notes, framework convention comments, examples that intentionally
  simplify internals, and speculative claims.
- Add or update prompt-regression fixture coverage so the labels and
  false-positive notes cannot silently drop.
- Refresh generated `.codex/prompts/` adapters through
  `make prompt-adapters-export`.

## Non-Goals

- No static stale-comment scanner, parser, or blocking CI gate.
- No automatic source comment/docstring edits.
- No repo-contract-kit or installed target-repo changes.
- No changes to AGW-044 learning-comments receipt semantics.
- No network, browser, hosted model, or GitHub API behavior.
- No treating every stale-looking comment as a defect.

## Acceptance

1. The `doc-code-delta` prompt explicitly reviews behavior-describing comments
   and docstrings for drift while keeping low-confidence cases advisory and
   non-blocking.
2. The finding template or synthesis guidance names comment/docstring drift
   labels and false-positive categories without a breaking schema change.
3. Every comment/docstring drift finding requires concrete evidence from the
   maintained comment/docstring and the current source of truth.
4. False-positive labels cover generated/vendor code, intentional historical
   notes, examples that intentionally simplify implementation details,
   framework convention comments, and speculative or low-confidence drift.
5. The final diff does not add a scanner, CI gate, repo-contract-kit target, or
   automatic source-comment edit behavior.
6. Prompt adapters are regenerated and checked.
7. Prompt regression fixtures or equivalent focused tests include at least one
   advisory comment/docstring drift case with false-positive handling.
8. Docs, version, changelog, and backlog closeout are updated after validation.

## Required Validation

Run in agent-workflow-kit:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_prompt_regression_fixtures`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_prompt_regression_fixtures.py`
- `PYTHONDONTWRITEBYTECODE=1 make prompt-adapters-export`
- `PYTHONDONTWRITEBYTECODE=1 make prompt-adapters-check`
- `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
- `make docs-check`
- `python3 scripts/check_doc_impact.py`
- `make version-check`
- `git diff --check`
- `make backlog-check && make backlog-split-check` after closeout

## Closeout

- Record or link a final receipt at
  `.agent-workflows/tasks/agw-031-comment-docstring-drift/receipt.json` or a
  durable sidecar equivalent.
- Run or record why unavailable:
  `make agent-task-ready TASK=AGW-031 TASK_READY_JSON=1`.
- Finish any local task metadata with:
  `make agent-task-finalize TASK=AGW-031 TASK_RECEIPT=<path> TASK_FINALIZE_JSON=1`
  or the local lifecycle fallback.
- Final handoff must say whether the checkout is clean, only expected files
  remain dirty, cleanup is blocked, or unrelated dirt was preserved.
