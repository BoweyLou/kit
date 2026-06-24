# Agent Run Completion And Guardrails Research Packet

Date: 2026-06-22

Status: complete research packet, no shipped runtime behavior.

## Question

How should the workflow stack extend from "agents have good local commands" to
"agents reliably finish work in logical chunks, commit approved work, close task
state, and prune finished worktrees"?

This packet covers two requested areas:

- completion: task work is finished, committed when approved, metadata is
  terminal, receipts are linked, and eligible worktrees are pruned
- guardrails: every run follows a small repeatable set of gates, including
  docs/code alignment, without turning `AGENTS.md` into a long procedure dump

## Recommendation

Build one explicit start gate and one explicit finish gate, both backed by
machine-readable policy and receipts.

1. Add a finish command, tentatively `make agent-task-complete`, that composes
   existing task readiness, docs alignment, receipt validation, commit, task
   finalization, final task status, and closeout preview/apply evidence.
2. Add a docs alignment command, tentatively `make agent-docs-alignment`, that
   gives agents one clear answer: docs updated, no docs needed with a reason,
   semantic review needed, or blocked.
3. Add a run profile/checklist contract, tentatively
   `.agent-workflows/agent-run-profile.json`, that describes required gates for
   `orient`, `scope`, `implement`, `verify`, and `complete` phases.
4. Teach task packets to carry a compact chunk plan: one task, one bounded
   change, one validation path, one closeout path. Larger work should be split
   into phase files or separate packets before edits begin.

Do not solve this by adding many more prose rules to `AGENTS.md`. The elegant
shape is a short route in `AGENTS.md`, a deterministic profile file, and local
commands that tell the agent the exact next step.

## Source Evidence

External primary sources:

- Git's `git-worktree` manual states that linked worktrees should be removed
  with `git worktree remove`; if a worktree directory was deleted manually,
  `git worktree prune` cleans stale administrative files. The same page says
  `remove` only accepts clean worktrees unless force is used, and the main
  worktree cannot be removed:
  <https://git-scm.com/docs/git-worktree>.
- GitHub protected branch docs show the general merge-gate model: required
  status checks must reach an accepted status before protected-branch changes,
  and strict checks require the branch to be up to date before merging:
  <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches>.
- GitHub merge queue docs reinforce the same design point for queued work:
  required checks must report on merge-group events, or queue integration fails:
  <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue>.
- GitHub required-check troubleshooting documents a practical hazard for path
  filtering: skipped required workflows can stay pending, while skipped jobs can
  report success. Local gates should therefore avoid "silent skip" ambiguity:
  <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks>.

Local evidence:

- `scripts/agent_task_prepare.py` already creates isolated branches/worktrees,
  task packets, receipt templates, metadata, owner/session fields, dirty-primary
  baselines, and overlap warnings.
- `scripts/agent_task_ready.py` already checks declared task scope against
  changed files, receipt evidence, docs impact, branch freshness, active task
  overlap, and dirty-primary baseline drift.
- `scripts/agent_task_finalize.py` already composes readiness, lifecycle
  transition, task status, closeout preview, and finalizer receipt output.
- `scripts/agent_task_cleanup.py` already classifies worktrees, detects nested
  pools, inventories terminal task worktrees, and only removes closeout
  candidates through explicit apply behavior.
- `scripts/check_doc_impact.py` already detects path-based docs impact and
  supports an explicit `No docs needed:` declaration.
- `scripts/check_docs_freshness.py` already checks local links, documented Make
  targets, script references, schema references, and optional semantic receipt
  requirements.
- `docs/harness-engineering.md` already frames task startup as closeout-first
  and names previous task closeout, docs impact, docs freshness, task readiness,
  receipts, state ledger, and closeout as harness evidence.
- `.agent-workflows/agent-permission-policy.json` currently treats git commit
  as approval-required for write workers. Any "ensure committed" path therefore
  needs an explicit packet/profile approval field rather than hidden commits.

## Current Gap

The stack has the parts, but no single authoritative "exit ramp".

Agents can run readiness, docs checks, receipt validation, lifecycle finish,
task status, and closeout separately. In practice, that means a worker can stop
after tests pass but before:

- docs/code alignment is proven
- final receipt is valid
- the intended diff is committed
- task metadata is terminal
- a closeout preview is recorded
- eligible worktrees are removed or intentionally retained

The second gap is cognitive. Agents see many good commands, but not a small
stage-based contract that says: "For this kind of run, these are the required
steps, and this command proves whether you are done."

## Proposed Architecture

### Start Gate: Run Profile Plus Chunk Plan

Add an installed run profile such as:

```json
{
  "schema_version": 1,
  "profiles": {
    "write-worker": {
      "orient": ["agent-start", "kit-status", "agent-task-status"],
      "scope": ["agent-task-packet", "goal-check", "docs-alignment-plan"],
      "implement": ["stay-within-allowed-files", "heartbeat"],
      "verify": ["docs-alignment", "agent-verify", "version-check-if-needed"],
      "complete": ["agent-task-complete"]
    }
  }
}
```

This should be data, not a prompt essay. `AGENTS.md` can route to the profile;
the command prints the relevant slice for the current phase.

Task packets should also gain a compact `chunk_plan`:

```json
{
  "chunk_plan": {
    "max_change_shape": "one behavior or one docs-contract slice",
    "phase_files_required": false,
    "chunks": [
      {
        "id": "docs-alignment-gate",
        "objective": "compose doc-impact, freshness, semantic receipt state",
        "allowed_files": ["scripts/", "docs/", "tests/"],
        "validation": ["focused tests", "make docs-check"],
        "completion_evidence": ["docs alignment receipt", "task receipt"]
      }
    ],
    "split_when": [
      "more than one user-visible behavior changes",
      "scope crosses unrelated area contracts",
      "validation cannot fit one receipt",
      "docs policy and implementation both need independent review"
    ]
  }
}
```

The point is not arbitrary file or line limits. The point is that every chunk
has one objective, known allowed files, validation, docs impact, and closeout
evidence before implementation begins.

### Docs Alignment Gate

Add `make agent-docs-alignment` as a deterministic aggregate over existing
docs checks.

Inputs:

- changed files from working tree, staged diff, branch range, or task worktree
- `doc-contract.json`
- optional `.agent-workflows/docs-alignment-policy.json`
- docs-impact output
- docs-freshness output
- optional docs-as-tests output
- optional semantic receipt path for higher-risk docs/code changes
- optional `No docs needed:` reason

Output states:

- `passed`: code and docs evidence are aligned for the declared scope
- `needs-docs`: relevant code/config/CLI/API/ops behavior changed and docs are
  missing
- `needs-semantic-review`: path coverage exists, but policy requires a semantic
  doc-code review receipt
- `no-docs-needed`: explicit waiver with a non-empty reason is accepted
- `blocked`: checker could not inspect the diff, config is invalid, or evidence
  is ambiguous

The command should preserve the existing docs stack instead of replacing it:

- `check_doc_impact.py` remains the path/category gate
- `check_docs_freshness.py` remains the local truth-surface gate
- `docs-as-tests` remains opt-in explicit-claim evidence
- semantic doc-code receipt stays policy-driven and high-signal

Integration points:

- `agent-task-ready` should consume the alignment receipt for task worktrees
- `agent-branch-readiness` should consume the same receipt for branch/PR
  handoff
- `agent-task-complete` should refuse to commit or finish when alignment is
  `needs-docs`, `needs-semantic-review`, or `blocked`

### Finish Gate: Agent Task Complete

Add `make agent-task-complete TASK=<id> TASK_RECEIPT=<path>` as the single
normal closeout command for approved write-worker tasks.

Suggested flow:

1. inspect task metadata and declared approval state
2. run `agent-docs-alignment`
3. run strict receipt validation
4. run task readiness
5. run configured validation commands or verify a receipt saying why skipped
6. if `COMMIT=1` and packet/profile permits commit, create a local commit from
   declared task files only
7. run task finalizer
8. run final task status with closed tasks included
9. run closeout preview
10. if `CLOSEOUT_APPLY=1`, remove only eligible clean terminal worktrees
11. run `git worktree prune -n` first, then apply stale-admin pruning only with
    an explicit `PRUNE_APPLY=1` flag
12. emit one completion receipt with every substep and final repository state

Default behavior should be conservative:

- no commit unless `COMMIT=1` and task packet says commit is approved
- no push
- no forced worktree removal
- no forced prune
- no deletion of dirty, unmerged, unknown, locked, or receiptless worktrees
- no closeout apply unless explicit

Completion should be allowed to fail cleanly. A blocked completion receipt is
better than a half-finished run with no durable explanation.

### Commit Policy

The current permission profile makes commit approval-required. Preserve that.

Add packet/profile fields such as:

```json
{
  "completion_policy": {
    "commit": {
      "allowed": true,
      "mode": "local-only",
      "message_template": "<task-id>: <imperative summary>",
      "stage_only_declared_scope": true,
      "require_clean_after_commit": true,
      "push_allowed": false
    },
    "closeout": {
      "preview_required": true,
      "apply_allowed": true,
      "prune_stale_admin_allowed": true
    }
  }
}
```

This gives agents permission in a narrow, auditable way. They do not infer that
"finish the task" means "stage everything" or "clean all worktrees".

### Worktree Pruning Policy

Use two different words carefully:

- `git worktree remove`: remove a real linked worktree directory
- `git worktree prune`: remove stale Git administrative metadata for worktrees
  whose directories are already gone

Closeout should primarily call `git worktree remove` on clean, terminal,
known-task worktrees. `git worktree prune` should be a separate stale-admin
cleanup step, always previewed first with `-n`.

Eligible worktree removal requires:

- terminal metadata: done, blocked, or abandoned
- linked final receipt unless explicitly waived
- clean worktree status
- branch head reachable from primary `HEAD` or otherwise explicitly retained
- no active task overlap
- path inside known task worktree pool
- not locked
- not main worktree
- no submodule or unavailable-status ambiguity

If any condition fails, the closeout receipt should say why the worktree was
retained and what the operator should do next.

## UX Shape

The agent-facing workflow should be short:

```bash
make agent-start
make agent-task-packet
make agent-task-prepare TASK=<id> SCOPE=<paths>
# work in the task worktree
make agent-task-complete TASK=<id> TASK_RECEIPT=<path> COMMIT=1
```

When the command refuses, it should print one next command, not a wall of
policy:

- `Run make agent-docs-alignment DOCS_SEMANTIC_RECEIPT=<path>`
- `Add docs or record No docs needed: <reason>`
- `Run make agent-task-ready TASK=<id> TASK_RECEIPT=<path>`
- `Run make agent-task-finalize TASK=<id> TASK_RECEIPT=<path>`
- `Run make agent-task-closeout TASK_CLOSEOUT_JSON=1`

The full receipt can carry all details for audit.

## Guardrails That Should Be Enforced

Every write-worker run should prove:

- orientation happened from live state
- exactly one scoped task or phase was selected
- declared scope and actual changed files match
- docs/code alignment passed or has an accepted explicit waiver
- behavior-changing work has test evidence or a grounded skip reason
- receipt is valid
- local commit exists when the packet/profile required a commit
- task metadata is terminal or blocked with a durable receipt
- closeout preview ran
- worktree cleanup was applied or intentionally retained with reasons

These should be command outputs and receipt fields, not just prompt language.

## Proposed Backlog Shape

Use these as candidates after deciding whether the previously recommended
Make-surface reconciliation remains `AGW-102`.

### Candidate 1: Agent Task Complete

- Proposed ID: `AGW-103`
- Priority: `P0`
- Repo: `repo-contract-kit`
- Theme: `completion`
- Item: Add `agent-task-complete` as the single write-worker finish gate for
  docs alignment, strict receipt validation, task readiness, optional approved
  commit, task finalization, task status, and closeout preview/apply.
- Why: Existing commands are individually useful but too easy to stop before
  commit, finalizer, and closeout evidence.
- Delivery shape: CLI and Make target, completion receipt schema, local-only
  commit policy, no push, no forced cleanup, tests for pass/blocked/commit
  denied/closeout retained cases, docs and version update.

### Candidate 2: Docs Alignment Aggregate

- Proposed ID: `AGW-104`
- Priority: `P0`
- Repo: `repo-contract-kit`
- Theme: `docs contract`
- Item: Add `agent-docs-alignment` and optional docs alignment policy so agents
  get one deterministic pass/needs-docs/needs-semantic-review/waived/blocked
  result.
- Why: `docs-check` proves several useful things, but agents still need a
  compact "am I allowed to finish this task?" docs/code alignment answer.
- Delivery shape: aggregate command over docs-impact, docs-freshness,
  docs-as-tests, semantic receipt policy, and No-docs-needed reason; integrate
  with task-ready, branch-readiness, and task-complete.

### Candidate 3: Run Profile And Chunk Plan

- Proposed ID: `AGW-105`
- Priority: `P1`
- Repo: `repo-contract-kit/workflows` and installer templates
- Theme: `operator clarity`
- Item: Add an agent run profile plus task-packet `chunk_plan` so agents work
  in logical, manageable slices and know the required gates for each phase.
- Why: The stack has many commands; a stage profile turns them into a small
  workflow without bloating `AGENTS.md`.
- Delivery shape: schema, example profile, task packet field, prompt updates,
  generated adapters/templates, tests for missing chunk plan and oversized
  scope escalation, docs.

### Candidate 4: Worktree Retention Sweep

- Proposed ID: `AGW-106`
- Priority: `P1`
- Repo: `repo-contract-kit`
- Theme: `isolation`
- Item: Extend closeout with an explicit retention sweep for eligible terminal
  task worktrees and stale Git worktree administrative records.
- Why: `agent-task-closeout` exists, but completion needs a stronger retained
  versus removed explanation and a safe stale-admin prune path.
- Delivery shape: closeout receipt expansion, `git worktree prune -n` preview,
  explicit apply flags, locked/missing/dirty/unmerged cases, docs and tests.

## Recommended Sequence

1. Build `AGW-104` first if the immediate pain is docs/code drift. It is the
   cleanest, smallest enforcement surface and can feed existing readiness
   checks.
2. Build `AGW-103` next. It becomes the normal finish command and consumes the
   docs alignment result.
3. Build `AGW-105` after the finish gate exists, so the run profile can point
   to real commands.
4. Build `AGW-106` only if `AGW-103` reveals closeout/prune cases that are not
   already handled cleanly by `agent-task-closeout`.

## Validation Plan

For `repo-contract-kit` implementation:

- focused unit tests for each new command and policy branch
- fixture repos for docs-needed, docs-waived, semantic-needed, and docs-passed
  changes
- fixture task worktrees for completion pass, missing receipt, scope drift,
  dirty worktree, commit denied, commit allowed, closeout retained, closeout
  removed, stale-admin prune preview, and locked worktree
- `make test`
- `make docs-check`
- `make version-check`
- `git diff --check`

For this source/legacy checkout if prompts or task-packet schema change:

- `make prompt-adapters-export`
- `make validate`
- `make agent-verify`
- `make backlog-check`
- `make backlog-split-check`
- `git diff --check`

## Stop Conditions

- Stop if the design requires agents to force-remove worktrees, reset branches,
  stage unrelated files, push without explicit approval, or delete user work.
- Stop if docs alignment depends on broad prose inference instead of explicit
  local checks, explicit semantic receipts, or an accepted waiver.
- Stop if the run profile duplicates long procedure text already present in
  docs instead of routing to commands.
- Stop if commit policy cannot stage only declared task scope.
- Stop if closeout cannot distinguish "eligible to remove" from "retain and
  explain".

## Open Questions

- Should `COMMIT=1` be accepted from task-packet approval alone, or should the
  operator still pass a command flag every time? Recommendation: require both.
- Should closeout apply happen inside `agent-task-complete` or remain a second
  explicit command? Recommendation: preview inside complete, apply only with an
  explicit flag.
- Should docs semantic receipts become mandatory for all behavior changes or
  only configured high-risk categories? Recommendation: policy-driven high-risk
  categories first.
- Should this be built entirely in `repo-contract-kit`, or should source prompts
  in this legacy checkout also change? Recommendation: installed behavior
  belongs in `repo-contract-kit`; only change source prompts here if the
  workflow-source consolidation has not yet moved the relevant files.
