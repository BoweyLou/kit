# Working Rhythm

Use this page when the command list feels wider than the workflow.

For the maintainer ownership map, start with
[`docs/agent-workflow-stack.md`](agent-workflow-stack.md).
For the agent-harness component map, use
[`docs/harness-engineering.md`](harness-engineering.md).

For normal target-repo use, the product surface is one command-line tool:

```bash
curl -fsSL https://raw.githubusercontent.com/BoweyLou/repo-contract-kit/main/install.sh | sh
kit setup --preset agentic
```

After that, use `kit status` and `kit update` for repo management, and
`kit doctor` for non-mutating diagnostics. `kit setup` is a two-word command:
the installed launcher is `kit`, and `setup` is its subcommand. Target repos
should not need to know that this workflow-source repo exists.

Maintainers still need to know the current implementation layers during the
legacy archive window:

- `repo-contract-kit/workflows/` is the live workflow source. It owns prompts,
  personas, schemas, review patterns, task-packet guidance, and the portable
  docs that explain how agent work should run.
- `repo-contract-kit` is also the install layer. It copies guardrails, scripts,
  Make targets, permissions, receipts, and prompt snapshots into target repos.
- this checkout is legacy source history for migration evidence and archive
  validation.
- An installed target repo is where normal work happens. It uses local commands
  such as `make agent-start`, `make agent-task-packet`,
  `make agent-task-status`, `make agent-task-prepare`, and
  `make agent-verify`.

Do not expose legacy source history as the normal operator rhythm. New source
work starts in `repo-contract-kit/workflows/`.

## Four Moves

### 1. Orient

Use this when returning to a repo or starting a new session.

```bash
make agent-start
make kit-status
make agent-next
```

`agent-start` writes a local packet with changed files, docs impact, latest ADR
context, kit/version state, review risk, recommended prompts, and a receipt
template. `agent-context-bundle` is the compact deterministic report to inspect
first when installed by a current `repo-contract-kit`; it combines dirty state,
backlog/next work, task status, docs impact, goal check, token budget, sidecar
paths, readiness hints, and omissions. `kit-status` tells you whether the
installed guardrails are current
and whether files have drifted. `agent-next` combines backlog state, dirty
working tree state, and active task metadata when you need the next safe
handoff. If a compact report is missing, stale, blocked, ambiguous, or omits a
required field, inspect the scoped source files needed to fill the gap and
record the omission.

### 2. Review

Use this when the goal is understanding, review, or finding risk before edits.

```bash
make agent-run-review AGENT=manual
```

Manual mode creates reviewer prompts and local JSON artifacts. For new
workflow-source edits, use the live source in the companion `repo-contract-kit`
repo's `workflows` directory. In this legacy checkout, use `workflows/prompts/`
or `.codex/prompts/` only as archive or migration evidence.

### 3. Scope

Use this when a backlog row, accepted finding, issue, or broad human request
needs to become executable work.

```bash
make agent-task-packet
make backlog-status
make agent-task-packet-from-backlog BACKLOG_ID=<id>
```

The task packet names the repo goal, affected area contracts, alignment
decision, previous task state, closeout-before-start decision, allowed files,
non-goals, docs impact, validation, risk, approval state, and closeout
requirements. It keeps planning input from turning into an unbounded
implementation request and makes final receipt, readiness, lifecycle,
task-status, closeout-preview, and dirty-state evidence part of the handoff
contract. If alignment is unknown, conflicting, or requires goal adaptation, or
if previous task state is missing, blocked, dirty, stale, or ambiguous, the
packet stops or escalates before implementation handoff. Installed targets with
a backlog source can also report backlog health, map changed paths through
`goal-check`, and scaffold a packet from one stable backlog id.

For large reviews or implementations, the task packet can include
`phase_files`. Use phase files only when one approved packet is still the right
scope but a fresh agent session needs a smaller bounded phase. Each phase names
its objective, allowed scope, completion evidence, and handoff notes. Phase
files preserve continuity; they do not replace the task packet, widen scope, or
approve work beyond the packet.

For recurring research-backed backlog work, scope starts with the research
brief's novelty ledger. The loop should compare the question against prior
fingerprints and recent topics, score several candidate ideas during synthesis,
reject low-novelty repeats, and carry rejected or deferred leads into the next
brief instead of repeatedly proposing the same backlog edits.

### 4. Execute

Use this after the task is approved for write-capable work.

```bash
make agent-task-status
make agent-task-cleanup
make agent-task-prepare TASK=<id> SCOPE=<paths>
make agent-task-heartbeat TASK=<id>
make agent-task-finish TASK=<id> TASK_RECEIPT=<path>
make agent-task-closeout
make agent-verify
```

In installed target repos, `agent-task-status` shows active task scopes,
registered git worktrees, dirty or missing task worktrees, and coordination
hazards. `agent-task-cleanup` audits confusing or nested task worktrees before
layout repair. `agent-task-prepare` creates a task branch and sibling worktree,
writes task artifacts, and records local in-flight metadata with run id,
owner/session, heartbeat, and lease fields. The worker edits in that isolated
worktree only after the task packet records a `safe-start` prior-closeout gate,
refreshes long-running leases with `agent-task-heartbeat`, and closes metadata
with `agent-task-finish`, `agent-task-block`, or `agent-task-abandon`. If prior
state is unresolved, the worker should refuse or escalate before edits and name
the needed finalizer, task-status, closeout preview, self-heal, blocker receipt,
or owner action. Where the installed kit exposes the task finalizer, use it to
combine readiness, lifecycle, final status, and closeout-preview evidence before
handoff. After final receipt evidence is durable and the task branch is
reviewed or merged, `agent-task-closeout` previews finished sibling worktrees
that can be removed; set `TASK_CLOSEOUT_APPLY=1` only after reviewing the dry
run. `agent-verify` is the local gate before handoff.
In this source repo, that gate includes prompt-adapter sync, backlog split
checks, agentic regression fixtures, docs-impact benchmarks through the test
suite, and the prompt regression fixture runner.
For evidence-heavy handoffs, use
[`docs/codex-review-trace.md`](codex-review-trace.md) as the CLI-later contract
for composing receipts, summaries, task packets, context reports, task-status,
state-ledger, and closeout/finalizer evidence. No `codex-review trace` command
or Make target ships from this source repo today.
The installed task prepare/status commands share task-scope parsing and overlap
checks through `scripts/_agent_scope.py`, so update that helper in the kit
source when the scope contract changes.

When using multiple Codex terminals, run the prepare command from the main
checkout in each terminal, then `cd` into the worktree path printed for that
task. You keep using the same Codex terminal after the `cd`; the main checkout
is only the coordination point.

## Common Paths

For a quick orientation pass:

```bash
make workflow-help
make agent-start
make kit-status
make stack-status KIT=/path/to/repo-contract-kit
make agent-next
```

For a read-only review:

```bash
make agent-start MODE=drift
make agent-run-review AGENT=manual
make agent-receipt-verify
```

For an accepted implementation task:

```bash
make agent-task-packet
make backlog-status
make agent-task-status
make agent-task-prepare TASK=<id> SCOPE=<paths>
```

For documentation and context-size gates:

```bash
make docs-freshness
make agent-token-budget
make skill-pack-export
make skill-pack-check
```

`make skill-pack-export` writes an ignored Codex skill-pack projection under
`dist/codex-skill-pack/` by default. Use `make skill-pack-list` to inspect the
configured skill names, and set `SKILL_PACK_OUTPUT` only when you explicitly
want the artifact somewhere else.

For maintenance of the installed kit:

```bash
kit status
kit update --dry-run
kit update
kit doctor
```

Use the global CLI for ordinary target-repo maintenance. Keep kit updates
explicit; normal validation should not update installed guardrails
automatically. When the global CLI is unavailable, `make kit-update
KIT=/path/to/repo-contract-kit` and `make kit-refresh
KIT=/path/to/repo-contract-kit` remain local-checkout fallbacks. The old
stack-update path is now a maintainer compatibility shim, not a normal target
workflow.

## Where To Go Next

- Use `README.md` for the project overview and source repo layout.
- Use `.agent-workflows/README.md` for local mechanics and file locations.
- Use `docs/using-the-prompt-kit.md` for prompt-level recipes.
- Use `docs/worktree-per-task-runner.md` for isolated write-worker details.
- Use `docs/local-tool-agnostic-plan.md` for the broader design constraints.
