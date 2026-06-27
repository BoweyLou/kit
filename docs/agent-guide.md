# Agent Guide

Use this page when an agent or automation is operating a repo with kit.

## Machine Rule

Do not scrape README prose to infer command safety.

Use structured commands:

```bash
kit start --json
kit command-map --json
kit agent-context --json
kit agent-tool-manifest --json
```

`kit start --json` is the first route selector. In installed target repos it
may apply an already-local, local-safe kit update before returning the journey.
The command metadata includes audience, route role, mutation behavior, sidecar
write behavior, target repo write behavior, examples, docs, and output schema
names. `kit agent-context --json` is a compatibility alias for
`kit command-map --json`; use
`agent-context-bundle` or `make agent-context-bundle` when you need repo handoff
context.

## Startup

From the target repo:

```bash
kit start --json
kit start --no-update --json
kit start --update-policy check-only --json
kit status --json
kit mode-check --json
```

If the target repo has kit installed and you need a local startup packet, use
`make agent-start` after reading `kit start --json`. If you need compact handoff
context, use `make agent-context-bundle`.

If `kit` is not available but this checkout is local, use:

```bash
python3 /path/to/kit/scripts/repo_contract_kit.py start --repo /path/to/repo --json
python3 /path/to/kit/scripts/repo_contract_kit.py command-map --json
```

Treat direct `python3 scripts/repo_contract_kit.py ...` calls as a
source-checkout fallback, not the preferred target-repo route.

Treat `kit start --json` as the first startup payload when the current repo
state is unknown. It returns `repo_role`, a `journey`, selected `mode`,
`local_update` details, write metadata, human-readable `next_steps`,
audience-specific `human_next_commands` and `agent_next_commands`, plus
`mode_next_commands` for the selected harness validation path.

Use `kit start --no-update --json` when the agent must guarantee no target
writes. Use `kit start --update-policy check-only --json` when the agent should
inspect whether a local update is available without applying it. Remote fetches
and global tool refreshes are never part of `kit start`; run
`kit update --global` only when a human asks to refresh the global checkout.

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
`local_update`, `target_repo_writes`, `sidecar_writes`, `next_commands`, and
`exit_code`.

## Sidecar Artifacts

Some commands can write repo-external sidecar artifacts when explicitly asked.
Use sidecar writes for startup packets, proposals, automation handoffs, and
local evidence that should not be checked into the target repo.

Do not assume sidecar writes are target repo writes. Keep those surfaces
separate in receipts and summaries.

## Safe Defaults

- Treat dirty target work as a blocker unless the command says it is read-only
  or reports an applied local-safe managed-file update.
- Preserve target-owned files.
- Never copy `.doc-contract-kit/updates/<stamp>/proposed/` wholesale.
- Keep root `AGENTS.md` in the target repo root.
- Use `kit start --no-update --json` for a guaranteed no-write startup payload.
- Use `kit update --dry-run --json` before `kit update`.
- Use `kit verify --harness-mode auto --json` before finalizing work.

## Command Reference

Use [cli-reference.md](cli-reference.md) for human-readable generated docs and
`kit command-map --json` for exact machine metadata.
