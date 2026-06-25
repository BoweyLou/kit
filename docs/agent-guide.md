# Agent Guide

Use this page when an agent or automation is operating a repo with kit.

## Machine Rule

Do not scrape README prose to infer command safety.

Use structured commands:

```bash
kit command-map --json
kit agent-context --json
kit agent-tool-manifest --json
```

The command metadata includes audience, route role, mutation behavior, sidecar
write behavior, target repo write behavior, examples, docs, and output schema
names.

## Startup

From the target repo:

```bash
kit agent-context --json
kit status --json
kit mode-check --json
```

If `kit` is not available but this checkout is local, use:

```bash
python3 /path/to/kit/scripts/repo_contract_kit.py agent-context --repo /path/to/repo --json
```

## Choose Work Weight

Always let the selector report the minimum safe harness mode:

```bash
kit mode-check --json
```

Use the selected mode unless a human asks for a stricter one. Do not downgrade
when the payload reports blockers.

## Plan And Verify Work

For normal work:

```bash
kit task-packet --harness-mode auto --json
kit verify --harness-mode auto --json
```

For backlog-led work:

```bash
kit backlog-status --json
kit agent-next --json
kit agent-task-packet-from-backlog --backlog-id <id> --json
```

## Read-Only First

Prefer non-mutating commands before any write:

```bash
kit status --json
kit update-plan --json
kit update --dry-run --json
kit doctor --json
```

A command that writes should say so in structured output. Inspect
`target_repo_writes`, `sidecar_writes`, `next_commands`, and `exit_code`.

## Sidecar Artifacts

Some commands can write repo-external sidecar artifacts when explicitly asked.
Use sidecar writes for startup packets, proposals, automation handoffs, and
local evidence that should not be checked into the target repo.

Do not assume sidecar writes are target repo writes. Keep those surfaces
separate in receipts and summaries.

## Safe Defaults

- Treat dirty target work as a blocker unless the command says it is read-only.
- Preserve target-owned files.
- Never copy `.doc-contract-kit/updates/<stamp>/proposed/` wholesale.
- Keep root `AGENTS.md` in the target repo root.
- Use `kit update --dry-run --json` before `kit update`.
- Use `kit verify --harness-mode auto --json` before finalizing work.

## Command Reference

Use [cli-reference.md](cli-reference.md) for human-readable generated docs and
`kit command-map --json` for exact machine metadata.
