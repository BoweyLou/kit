# AGW-125 Task Packet: Legacy Runtime And Prompt Docs

## Source

- Backlog item: `AGW-125`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Status: `done`

## Problem

Runtime adapter and prompt-kit docs still described this legacy checkout's
`workflows/prompts/` and `workflows/manifest.json` files as the current
canonical workflow source. After `AGW-100`, live prompt, schema, adapter, and
task-packet source edits belong in `repo-contract-kit/workflows/`.

## Scope

- Mark runtime adapter docs as legacy source-checkout documentation.
- Update runtime compatibility ownership, status legend, source-of-truth cells,
  and support summary to route current source edits to
  `repo-contract-kit/workflows/`.
- Mark prompt-kit usage docs as historical/manual recipes rather than live
  source instructions.
- Update the local tool-agnostic plan, README, and ADR wording so archive
  maintenance remains possible without presenting this checkout as current
  prompt source.

## Non-Goals

- Do not remove historical prompt links from this checkout.
- Do not migrate prompt source or generated adapters as part of this docs-only
  cleanup.
- Do not change `repo-contract-kit` behavior or installed target files.

## Validation

- `python3 scripts/check_doc_impact.py --working-tree`
- `make docs-check`
- `make agent-docs-lint`
- `git diff --check`

## Closeout Evidence

- `README.md`, `docs/runtime-adapters.md`, `docs/runtime-compatibility.md`,
  `docs/using-the-prompt-kit.md`, `docs/local-tool-agnostic-plan.md`, and
  `docs/adr/0002-self-dogfood-boundary.md` now distinguish live
  `repo-contract-kit/workflows/` source ownership from this checkout's
  legacy/archive material.
- A stale-ownership scan no longer finds the targeted current-tense phrases for
  canonical prompt source ownership in this checkout.
