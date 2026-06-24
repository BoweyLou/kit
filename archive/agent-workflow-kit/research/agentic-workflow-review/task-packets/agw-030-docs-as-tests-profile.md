# AGW-030 Task Packet: Docs-As-Tests Experimental Profile

## Task

- ID: `AGW-030`
- Title: Prototype docs-as-tests for API docs in an experimental profile.
- Priority: `P2`
- Repo: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- Status: approved
- Source: `research/agentic-workflow-review/backlog.csv:31`

Add an opt-in experimental docs-as-tests profile for API documentation. The
prototype should run only high-confidence, explicitly declared checks. It must
not scrape arbitrary Markdown prose, execute arbitrary examples, require
network access, or become part of the default or `agentic` presets.

## Safe Start Evidence

- Source main is clean and pushed at
  `5849f4f54bb299150dc2e0346e153f40a8ce5c2c`.
- Kit main is clean and pushed at
  `1a23bb0bb5b3d2f04077ddeacf512b260d9e3221`.
- Source `make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1
  TASK_STATUS_JSON=1` reports zero active tasks, no stale tasks, and no
  hazards.
- Source `make agent-next` selects AGW-030 with a clean checkout.
- Kit `make agent-task-status` is unavailable in the kit source checkout; treat
  that as an omitted installed lifecycle surface, not active task metadata.

Decision: safe-start.

## Implementation Scope

Allowed kit areas include:

- `scripts/check_docs_as_tests.py`
- `scripts/repo_contract_kit.py`
- `scripts/install.py`
- `templates/common/kit-makefile.mk`
- `templates/common/ops-agent-workflow.md`
- `templates/common/working-rhythm.md`
- `templates/profiles/docs-as-tests/`
- `README.md`
- `docs/rollout-guide.md`
- `docs/harness-engineering.md`
- `docs/roadmap.md`
- `CHANGELOG.md`
- `VERSION`
- focused tests such as `tests/test_docs_as_tests.py`,
  `tests/test_install.py`, and `tests/test_repo_contract_kit_cli.py`

Source closeout is limited to backlog, split backlog, summary, and feature
matrix files after kit validation passes.

Protected:

- agent-workflow-kit canonical prompts, schemas, and adapters
- default/minimal/agentic preset membership, unless the worker is only proving
  docs-as-tests remains absent from them
- target-owned `VERSION` and `CHANGELOG.md` in installed target repos
- network, browser, hosted model, GitHub API, or account dependencies
- unrelated backlog rows or unrelated dirty work

## Expected Shape

Preferred shape:

- Add an explicit experimental profile, likely `docs-as-tests`, installable via
  `python3 scripts/install.py <target> --profile docs-as-tests`.
- Install a small target config example, such as
  `.agent-workflows/docs-as-tests.json`, and operator guidance under
  `docs/ops/`.
- Add a deterministic local checker and expose it through the wrapper CLI and
  installed Make bridge, for example `repo_contract_kit.py docs-as-tests` and
  `make docs-as-tests`.
- Keep normal `docs-check` unchanged unless a target repo explicitly opts into
  the experimental profile/config.
- Support at least one API-doc-oriented high-confidence assertion, preferably a
  manifest-declared check that a documented HTTP method/path exists in a local
  JSON OpenAPI spec.
- Return JSON/text with assertion ids, source doc paths, spec paths, result,
  failures, omissions/refusals, `target_repo_writes=false`, and
  `network_used=false`.

Do not support heuristic prose scraping, YAML/OpenAPI completeness, generated
clients, live HTTP calls, external network checks, or arbitrary fenced code
execution in this slice.

## Acceptance

1. The experimental docs-as-tests profile installs explicitly and is not part
   of default/minimal/agentic presets.
2. The checker runs only config-declared high-confidence assertions and refuses
   unsupported, unsafe, ambiguous, or network-like inputs.
3. At least one API-doc assertion validates method/path presence in a local JSON
   OpenAPI spec, with pass and fail tests.
4. Output is deterministic and machine-readable, including assertion ids,
   source doc paths, artifact paths, result, failures, omissions/refusals,
   `target_repo_writes=false`, and `network_used=false`.
5. CLI and installed Make target expose the check without making it a default
   docs gate.
6. Docs explain how the experimental profile relates to `docs-freshness`,
   `docs-impact`, `docs-propose`, and semantic receipt review.
7. `VERSION` and `CHANGELOG.md` record the repo-contract-kit behavior/profile
   change.
8. Source backlog rows and summary close AGW-030 only after kit validation.

## Required Validation

Run in repo-contract-kit:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_as_tests tests.test_install tests.test_repo_contract_kit_cli`
- `PYTHONDONTWRITEBYTECODE=1 make test`
- `make docs-check`
- `make docs-freshness`
- `make version-check`
- `git diff --check`
- Install smoke: install `--profile docs-as-tests` into a temporary git repo,
  then run the installed docs-as-tests target or equivalent against a sample
  config/spec.

Run in the source repo after closeout:

- `make backlog-check`
- `make backlog-split-check`
- `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
- `git diff --check`

## Non-Goals

- No arbitrary Markdown code execution.
- No heuristic claim extraction from prose.
- No network, browser, hosted model, live server, GitHub API, or account calls.
- No default or `agentic` preset inclusion.
- No full OpenAPI/YAML validation or generated-client testing.
- No weakening of existing docs-impact, docs-freshness, docs-propose, or
  semantic receipt gates.
