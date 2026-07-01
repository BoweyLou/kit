# ADR 0003: Closeout Fix App Write Exception

## Status

Accepted

## Context

Kit Companion has intentionally been a read-only and preview-first app surface.
That boundary keeps repo mutation visible in terminal workflows and prevents
the app command browser from becoming a broad write-capable launcher.

Dirty repo closeout is different from ordinary command execution. Operators
need one action that can hand a selected repo to a supervised agent, preserve
semantic work, create commits, write receipts, prune only clean disposable
worktrees, verify strict closeout, and push without broad destructive cleanup.

## Decision

Keep the generic Kit Companion command browser read-only or preview-only.
Create one dedicated write-capable exception for `kit closeout-fix --repo
<repo> --apply --jsonl`.

The app exception uses a separate runner path and an allowlist that requires:

- command path `closeout-fix`
- `--repo <selected-target>`
- `--apply`
- `--jsonl`

The app runner rejects custom agent commands, arbitrary mutating flags, and
generic command-browser attempts to run `--apply`. The CLI remains the
authoritative implementation. `closeout-fix` preview stays read-only with
`kit closeout-fix --repo <repo> --json`.

## Consequences

Kit Companion gains a confirmed guided closeout workflow without making the
command browser a general mutation surface.

The closeout job still relies on CLI receipts, sidecar artifacts, strict
`closeout-plan` verification, and non-force Git push semantics. Failures are
shown as blockers instead of a successful app state.
