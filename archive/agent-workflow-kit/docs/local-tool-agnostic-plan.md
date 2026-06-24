# Local Tool-Agnostic Agent Workflow

This kit must work in locked-down repositories where GitHub Actions, hosted
agents, and cloud CI are unavailable. The baseline is a local checkout, a shell,
Git, and whichever coding agent the developer is allowed to use.

## Operating Contract

- Local first: every workflow must run from the filesystem and local shell.
- Tool agnostic: prompts and schemas must be usable from Codex, AmpCode, Claude
  Code, Aider, Cline, or a human terminal session.
- Cross-repo aware: work that touches installation, target-repo managed files,
  workflow source, or runtime adapters must start from the live
  `repo-contract-kit` owner and use this legacy checkout only for archive or
  migration comparison.
- Hosted CI optional: GitHub Actions examples can exist later, but cannot be the
  required path.
- Read-only by default: reviewers inspect, run local checks, and write reports.
  Write-capable agents need an explicit scope and a human approval point.
- Evidence required: serious runs should produce a receipt with commands, files,
  docs impact, tests, findings, and disposition.

## Recommended Local Flow

1. When the command surface is unfamiliar, run `make workflow-help` or read
   `docs/working-rhythm.md` to anchor the orient, review, scope, execute flow.
2. When installed through repo-contract-kit, start with `make agent-start` to
   generate the local session packet, latest ADR context, kit/update status,
   target repo version, recommended prompts, persona suggestions, and receipt
   template.
3. Run or inspect the local repo instructions: `AGENTS.md`, `REVIEW.md`, and any
   path-scoped rules.
4. Run local hygiene checks before asking an agent to reason broadly:
   `make kit-status`, `make docs-check`, local tests, and any
   agent-instruction lint target.
5. For backlog-driven work, use the installed task-packet command or the live
   `repo-contract-kit/workflows/prompts/task-packet.md` source before
   implementation so scope, validation, docs impact, risk, and approval state
   are explicit. Use this checkout's `workflows/prompts/task-packet.md` only as
   legacy comparison material.
6. For write-capable work, prepare an isolated worktree before editing. In
   installed target repos, use `make agent-task-prepare TASK=<id>` to create the
   task branch, worktree, local task packet, and receipt template.
7. Use the live `repo-contract-kit/workflows/prompts/personas/manifest.json` to
   choose a small reviewer set. The prompt source is intentionally tool-neutral;
   `.codex/prompts/` in this checkout is a legacy generated Codex adapter.
8. To materialize a local review run in an installed target repo, run
   `make agent-run-review AGENT=manual` for prompt/artifact generation or
   `make agent-run-review AGENT=amp` when Amp CLI should execute the read-only
   persona prompts through `amp --execute --stream-json`.
9. In this repo, run `make context-packet` before broad review work so changed
   files are paired with likely callers, tests, docs, ADRs, scripts, and runtime
   configs.
10. Ask each local agent/tool to return findings using
   `schemas/session-receipt.schema.json`.
11. Synthesize only evidence-backed findings. Suppress nits by default and use
   `schemas/review-synthesis.schema.json` for machine-readable synthesis.
12. For completed runs, render a concise handoff with
   `make receipt-summary RECEIPT=/path/to/receipt.json`.
13. For accepted code changes, use the TDD prompt set and capture red/green
   evidence in the receipt.
14. For behavior/API/config/runtime changes, run `make version-check` and decide
   whether `make version-bump BUMP=patch|minor|major` is in scope.
15. In this repo, install the tracked Git hook with `make install-git-hooks` so
   commits that touch prompts, schemas, scripts, examples, or governance files
   include `VERSION` and `CHANGELOG.md`.

## AmpCode and Codex Compatibility

AmpCode should use the same Markdown prompts and JSON schemas from the live
`repo-contract-kit/workflows/` source, or from this checkout only when the task
needs archive comparison. Codex can additionally use a generated native prompt
folder layout. The workflow should not depend on either tool being present for
local checks to run.

In target repos installed with `repo-contract-kit --preset agentic`,
`make agent-start` is the runtime-neutral startup bridge. It does not dispatch
or depend on a specific agent; it writes local artifacts that Codex, AmpCode, or
a human can read. `make agent-run-review` is the first executable bridge: manual
mode writes prompts and JSON placeholders, while Amp mode calls Amp's execute
interface and stores the raw and structured review artifacts locally.

The backlog surface is a task packet, not a separate backlog product. Keryx or a
repo mirror such as `docs/backlog.md` can hold prioritisation state; this kit
only standardizes the handoff from backlog item to executable agent work.

For write-capable work, pair the task packet with
`docs/worktree-per-task-runner.md`. The install layer owns the executable
`make agent-task-prepare TASK=<id>` command; this repo owns the portable
pattern and safety checklist.

For ongoing maintenance, `make kit-status` and
`make kit-update KIT=/path/to/repo-contract-kit` are the local-only update
bridge. Use `make kit-refresh KIT=/path/to/repo-contract-kit` when the local kit
checkout should be pulled fast-forward first and then applied through the same
safe updater. These commands avoid GitHub APIs, hosted CI, and destructive
overwrites by using the installed managed-file manifest.

## What Counts As Done

- The relevant local commands were run or a blocker was recorded.
- Documentation impact was checked locally.
- TDD evidence was captured when behavior changed and testing was practical.
- Findings have severity, confidence, evidence, and a disposition.
- No hosted CI or GitHub-only mechanism is required to understand the result.
