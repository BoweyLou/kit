# GitHub Copilot Instructions

This repository's durable agent instructions live in `AGENTS.md`.

For coding, review, and task handoff:

1. Read `AGENTS.md`, `REVIEW.md`, and `.agent-workflows/README.md`.
2. Respect the documentation contract in `doc-contract.json`.
3. Use `make agent-start`, `make docs-check`, and `make agent-verify` when those commands are installed.
4. Keep generated docs, changelog entries, and version files aligned with behavior changes.

Keep this file as a thin Copilot adapter. Put repository-specific rules in
`AGENTS.md` or scoped docs, not here.
