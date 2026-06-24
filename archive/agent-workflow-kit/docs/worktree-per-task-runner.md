# Worktree Per Task Runner

Use a separate Git worktree for every write-capable agent task when work may run
in parallel, when the main checkout has unrelated local work, or when the task
has a narrow approval boundary.

This pattern keeps review and planning local-first while giving write-capable
agents a clean place to edit files. Read-only reviewers should still use the
read-only sandbox policy. A worktree is for implementation after a task packet
or accepted finding has named the scope.

## Operator Flow

1. Select one backlog row, issue, accepted finding, or human request.
2. Convert it into a task packet with `workflows/prompts/task-packet.md`.
3. Check existing parallel work from the target repo with
   `make agent-task-status`.
4. Prepare a worktree from the target repo with
   `make agent-task-prepare TASK=<id>`.
5. Hand the generated task packet and receipt template to the write-capable
   worker.
6. Run validation inside the task worktree.
7. Re-check `make agent-task-status` before handoff so the worker sees active
   overlaps, stale metadata, and sibling worktree state.
8. Review the task branch before staging, committing, pushing, or merging.
9. Mark the local in-flight task metadata as done or remove the worktree when
   the task is closed.

If an existing repo already has nested or confusing task worktrees, start with
`workflows/prompts/task-worktree-cleanup.md`. In installed target repos that
have the cleanup script, `make agent-task-cleanup` audits the layout first and
only moves nested worktrees when explicit apply flags are set.

You can run the prepare command from inside an existing Codex terminal. You do
not need to open Codex after setup. Start in the main checkout, prepare the
task, then `cd` into the worktree path printed by the command and continue from
that same terminal session.

For two parallel Codex terminals:

1. Terminal 1 starts in the main checkout, runs `make agent-task-prepare
   TASK=<id> SCOPE=<paths> OVERLAP=block`, then changes into the printed
   worktree path.
2. Terminal 2 also starts from the main checkout, runs its own
   `make agent-task-prepare TASK=<other-id> SCOPE=<other-paths>
   OVERLAP=block`, then changes into its own printed worktree path.
3. After that, each Codex session edits only its assigned worktree. The main
   checkout remains the coordination point for `make agent-task-status`.

## Installed Command Shape

`repo-contract-kit` owns the installed target-repo command because it writes
target repo files and worktrees. The expected interface is:

```bash
make agent-task-status
make agent-task-cleanup
make agent-task-prepare TASK=AGW-061 SCOPE=scripts/agent_task_prepare.py
```

The status command should:

- read ignored in-flight task metadata from `.agent-workflows/tasks/`
- compare that registry with `git worktree list`
- report missing, stale, dirty, or untracked task worktrees
- report unknown active scopes and declared scope overlaps
- support JSON output and strict failure for local coordination gates

The prepare command should:

- require a clean main checkout unless the operator explicitly allows dirty
  setup
- create a branch named for the task, under the normal `codex/` branch prefix
- create the worktree outside the main checkout by default
- write a task packet and receipt template into an ignored local artifact
  directory
- record in-flight task metadata under `.agent-workflows/tasks/`
- warn or block when a new task overlaps another active task's declared scope

The cleanup command should:

- default to read-only inventory
- classify registered task worktrees as primary, keep, move-flat, or investigate
- identify nested `*-agent-worktrees` pools and their flat target paths
- move nested worktrees only through an explicit apply mode
- leave removal decisions to explicit `git worktree remove <path>` commands

## Scope Rules

Every prepared task needs an explicit scope when possible:

- `allowed_files`: files or directories the worker may edit
- `protected_files`: files or directories the worker must not edit
- `validation`: local commands that prove the task is done
- `docs_impact`: expected docs or a reason docs are not expected

If the scope is not yet known, the command may still create the worktree, but
the receipt and metadata should mark the scope as unknown. Unknown scope is a
warning because overlap checks cannot protect the repo.

## Safety Checklist

Before implementation starts:

- the main checkout is clean or the operator accepted the dirty-state risk
- the worktree path is outside the main checkout
- the task packet names the requested work and validation commands
- the receipt template records the `write-worker` trust profile
- overlap warnings are reviewed
- no staging, commit, push, PR comment, or merge happens without human approval

Before merge:

- `git status --short` in the task worktree is understood
- unrelated files are absent from the task diff
- required validation commands ran, or skips are recorded with reasons
- docs impact was checked
- receipt evidence points at the task branch and worktree
