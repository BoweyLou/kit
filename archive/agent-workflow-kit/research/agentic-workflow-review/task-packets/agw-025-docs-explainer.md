# AGW-025 Task Packet: Docs Explainer

## Task

- ID: AGW-025
- Priority: P2
- Repo: `/Volumes/Myrtle/Code/04_Code/Hermes/doc-contract-kit`
- Status: approved
- Source: `research/agentic-workflow-review/backlog.csv:26`

Add a local docs Q&A/readme explainer mode for repository docs. The mode should
help a developer understand repo policy before waiving docs work, asking for a
docs patch, or escalating to a reviewer. It must stay local-first and
non-mutating by default.

## Safe Start Evidence

- Source main is clean and pushed at `d86fd6dd55690391a35fbbf790190598b2b8a21a`.
- Kit main is clean and pushed at `aca8d0f2be2463755f3252d6ade79df542ed0692`.
- Source `make agent-task-status` reports zero active tasks and no coordination
  warnings.
- Source `make agent-next` selects AGW-025 with a clean checkout.

Decision: safe-start.

## Implementation Scope

Allowed kit areas include a read-only docs explainer/Q&A helper, wrapper CLI,
installed Make target, slash-command or working-rhythm docs if needed,
tests, `VERSION`, and `CHANGELOG.md`. Source closeout is limited to backlog,
repo split backlog, summary, and feature matrix after kit validation passes.

## Acceptance

1. A local helper produces deterministic text/JSON docs-explainer output from
   repo docs without calling a hosted model or mutating target files by default.
2. The helper accepts a question and optional focus/path filters, selects
   relevant README/docs/policy files, and reports citations or source paths so a
   local agent or human can ground the answer.
3. Output includes a ready-to-use local prompt or explainer brief for docs Q&A,
   waiver understanding, or docs-patch planning, with explicit uncertainty when
   no matching docs are found.
4. Wrapper CLI and installed Make target expose the helper.
5. Docs explain how the helper relates to `docs-impact`, `docs-propose`,
   `/waive-docs`, and `/add-docs`.
6. VERSION and CHANGELOG record the repo-contract-kit behavior change.
7. Source backlog rows and summary close AGW-025 only after kit validation.

## Required Validation

Run in repo-contract-kit:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_explain tests.test_repo_contract_kit_cli tests.test_install`
- `PYTHONDONTWRITEBYTECODE=1 make test`
- `make docs-check`
- `make docs-freshness`
- `make version-check`
- `git diff --check`

Run in the source repo after closeout:

- `make backlog-check`
- `make backlog-split-check`
- `PYTHONDONTWRITEBYTECODE=1 make agent-verify`
- `git diff --check`

## Non-Goals

- Do not implement hosted PR comment execution or GitHub API mutation.
- Do not generate uncited free-form answers as if they are authoritative.
- Do not write docs, waivers, task packets, `VERSION`, or `CHANGELOG.md` by
  default.
- Do not replace `docs-impact`, `docs-propose`, or explicit task-packet
  approval before write-capable docs changes.
