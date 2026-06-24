# ADR 0002: Self-Dogfood Boundary

## Status

Accepted

## Context

This repository is both a source repo and a target repo.

As legacy `agent-workflow-kit`, it keeps historical workflow prompts, schemas,
adapter generation, tests, and backlog evidence. After `AGW-100`, live workflow
source moved to `repo-contract-kit/workflows/`. As a repo-contract-kit target,
this checkout still uses installed guardrails for documentation impact, local
agent startup, instruction hygiene, evidence receipts, review policy, and
update receipts.

Those roles are useful together, but they can also blur the boundary. The most
important failure mode is treating generated or installed target-repo files as
the source of truth for the tool itself.

## Decision

`repo-contract-kit/workflows/` is the live workflow source for new prompt,
persona, schema, task-packet, and research workflow edits. In this checkout,
`workflows/prompts/` remains legacy archive and migration evidence.
`.codex/prompts/` is a generated mirror of that legacy tree and must stay in
sync through `make prompt-adapters-export` and `make prompt-adapters-check`
whenever archive-maintenance work edits it.

`repo-contract-kit` organizes this repository through guardrail files, scripts,
receipts, hooks, and Make targets. It must not redefine prompt source ownership,
silently refresh legacy prompt content, or run `kit-update` as part of normal
validation. Kit updates must not make this checkout the live workflow source
again.

The installed manifest is allowed to report exactly these localized
kit-managed files:

- `.agent-workflows/README.md`
- `.agent-workflows/repo-review.md`
- `AGENTS.md`
- `doc-contract.json`
- `docs/ops/agent-workflow.md`
- `scripts/verify_agent_receipt.py`

Those files are localized because this repository is a legacy workflow-source
checkout with extra archive and migration duties, not an ordinary target repo
consuming a vendored snapshot. The local repo-review prompt also participates in
this repository's instruction-hygiene gate, so small wording changes can keep
local verification clean without redefining the live shared source. The receipt
validator is localized here when source-side schema evidence grows ahead of the
installed kit snapshot, so validation can cover historical compatibility without
turning every archive check into a repo-contract-kit behavior update. The
operator workflow runbook is localized here only to document this checkout's
target-owned root `Makefile` wrapper strategy; ordinary target repos still use
the managed kit fragment as their source of installed Make targets.

The mechanical guard is `make self-check`, backed by
`scripts/check_self_dogfood_boundary.py`. `make agent-verify` and the local
pre-commit hook run it.

## Consequences

- Future agents get a deterministic failure if they try to make `.codex/prompts/`
  the prompt source or wire `kit-update` into ordinary validation.
- Intentional localizations are explicit instead of looking like unexplained kit
  drift.
- Kit updates stay opt-in through `make kit-update KIT=/path/to/repo-contract-kit`.
- `make kit-refresh KIT=/path/to/repo-contract-kit` is also opt-in; it only
  adds a clean fast-forward pull before the same safe update path.
- A future change that intentionally localizes another kit-managed file must
  update this ADR, `scripts/check_self_dogfood_boundary.py`, and its tests in
  the same patch.

## Alternatives considered

- Do not install repo-contract-kit into this repo. That would avoid self-dogfood
  complexity but would stop this tool from exercising its own target-repo
  guardrails.
- Treat all installed files as kit-managed. That is too risky here because this
  repo still carries historical prompt and workflow source files used for
  archive validation and migration comparison.
- Leave the boundary as prose only. That is weaker than a local check and easy
  for future agent work to miss.
