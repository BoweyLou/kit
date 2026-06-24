# AGW-123 Task Packet: Legacy Source Route Maps

## Source

- Backlog item: `AGW-123`
- Source repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Status: `done`

## Problem

Several agent-facing route maps still said this checkout's `workflows/prompts/`
tree was the canonical workflow source even though `AGW-100` moved live workflow
source to `repo-contract-kit/workflows/`. That stale wording could send agents
to the historical checkout for new prompt, persona, schema, or task-packet
source edits.

## Scope

- Update `AGENTS.md`, `.agent-workflows/README.md`, and Makefile prompt text to
  route new workflow-source edits to `repo-contract-kit/workflows/`.
- Keep this checkout's `workflows/prompts/` described as legacy/archive and
  migration evidence with `.codex/prompts/` as its generated mirror.
- Preserve local dogfood guardrail commands such as `make agent-verify`,
  `make agent-docs-localize`, `make self-check`, and `make kit-status`.
- Update the self-dogfood checker, ADR 0002, and the working-rhythm docs so
  automated guidance, decision history, and Makefile-facing docs match the
  route-map change.

## Non-Goals

- Do not delete historical prompts or generated Codex adapters.
- Do not change workflow adapter generation behavior.
- Do not run a kit update or move files between repositories.

## Validation

- `python3 -m unittest tests.test_check_self_dogfood_boundary`
- `make self-check`
- `make agent-docs-lint`
- `make docs-freshness`
- `make agent-verify`
- `git diff --check`

## Closeout Evidence

- Version: `agent-workflow-kit` `0.2.33`.
- `AGENTS.md` and `.agent-workflows/README.md` now point live workflow-source
  work to `repo-contract-kit/workflows/`.
- Makefile agent prompts no longer call this checkout's `workflows/prompts/`
  canonical source; they identify it as legacy/archive material.
- `docs/working-rhythm.md`, `scripts/check_self_dogfood_boundary.py`, its
  tests, and ADR 0002 now verify and document the legacy route instead of
  reinforcing the old canonical-source wording.
