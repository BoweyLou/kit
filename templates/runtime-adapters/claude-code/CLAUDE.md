# CLAUDE.md

@AGENTS.md

This repository's durable agent instructions live in `AGENTS.md`. The import
above keeps this Claude Code adapter aligned with the shared repo instructions.

Before editing:

1. Read `AGENTS.md`, `REVIEW.md`, and `.agent-workflows/README.md`.
2. Run `make agent-start` when the kit is installed.
3. Run `make agent-task-status` before launching parallel write work.
4. Run `make agent-task-ready` or `make agent-task-finalize TASK=<id>` before handoff when working from a task packet.

Keep this file as a thin Claude Code adapter. Put repository-specific rules in
`AGENTS.md` or scoped docs, not here.
