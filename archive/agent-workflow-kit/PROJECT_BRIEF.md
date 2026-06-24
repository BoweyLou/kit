# agent-workflow-kit

This kit provides portable prompts, schemas, and conventions for local
agentic software development workflows. It covers multi-agent codebase review,
learning-oriented codebase exploration, behavior-neutral explanatory comments,
TDD/executable specs, remediation planning, and verification.

It is designed for these operating modes:

- `bootstrap`: first pass over a new or greenfield repository where intent, docs, tests, and maintenance boundaries may not exist yet.
- `drift`: repeated review of an existing repository to identify documentation/code deltas, AI-generated code slop, duplication, dead code, missed reuse, and operational risk.
- `pull-request`: changed-file review that starts from a diff and expands only when the change crosses shared contracts.
- `release-gate`: broad review that can produce merge blockers, release blockers, and deferred cleanup.
- `learning-comments`: subagent-led pass that reads docs, latest ADRs, existing comments, and actual code before adding behavior-neutral comments for a developer still learning the codebase, or producing a separate plain-language note for non-developer explainability when inline comments would be noisy.
- `test-first`: executable-spec pass for implementing accepted changes through TDD, regression tests, characterization tests, contract tests, property/invariant tests, and test-quality review.

The prompt library lives in `.codex/prompts/`. That folder is a Codex-friendly
adapter, not a Codex-only requirement. AmpCode, Codex, Claude Code, Aider,
Cline, or a human reviewer can use the same Markdown prompts and JSON schemas.

The prompts are deliberately read-first and evidence-first: reviewers should
cite files, commands, and behavioral surfaces before proposing edits.

## Principles

- Prefer grounded findings over generic advice.
- Separate investigation from remediation.
- Keep agent scopes narrow enough that parallel reviewers do not duplicate each other.
- Treat documentation, tests, and runtime behavior as part of the codebase contract.
- Treat explanatory comments as maintained documentation: verify them against docs, ADRs, tests, and code before adding or updating them. When the useful explanation belongs to a non-developer note instead of source, keep it out of inline comments.
- Treat tests as executable documentation when behavior is being created, fixed, or refactored.
- Preserve user work and avoid broad rewrites unless the review evidence justifies them.

## Current Harness Surfaces

The source repo dogfoods the installed guardrail layer. Use `make agent-next`
to see the next open backlog item alongside dirty-state and active-task
metadata, `make backlog-status` / `make backlog-check` to verify portable
backlog shape, and `make agent-task-packet-from-backlog BACKLOG_ID=<id>` to
scaffold executable work from a stable row.

Write-capable work should use task metadata with lifecycle closeout:
`make agent-task-prepare`, `make agent-task-heartbeat`,
`make agent-task-finish`, `make agent-task-block`, and
`make agent-task-abandon`. Verification now includes docs-freshness and
token-footprint surfaces through `make docs-freshness` and
`make agent-token-budget`.

## Companion Repo

The companion install layer is
[repo-contract-kit](https://github.com/BoweyLou/repo-contract-kit). It installs
repo-local guardrails such as `AGENTS.md`, `REVIEW.md`, docs-impact checks,
instruction linting, Make targets, workflow profiles, and optional adapters into
target repositories.
