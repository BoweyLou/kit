# Human Guide

Use this page when you want to operate kit directly.

## First Install

Install the launcher once:

```bash
curl -fsSL https://raw.githubusercontent.com/BoweyLou/kit/main/install.sh | sh
```

Then enroll a target repo:

```bash
cd /path/to/repo
kit start
kit setup --preset lite
kit status
```

Use `--repo /path/to/repo` when you are not already inside the target repo.

## Choose A Preset

Start with `lite` for small repos and low-risk local work.

Use `agentic` when you expect agents to use task packets, receipts, review
workflows, or local startup packets regularly:

```bash
kit setup --preset agentic
```

Use optional profiles only when you know the repo needs them. Examples include
runtime adapters, private local context, Python or Node stack hints, or
docs-as-tests.

## Daily Commands

```bash
kit start
kit status
kit mode-check
kit update --dry-run
kit doctor
kit closeout-plan
```

Use `kit start` when you are unsure whether this is a fresh setup, normal
maintenance, dirty work in progress, or a release-sensitive change. It reports
the selected journey, the suggested mode, and the next human and agent commands.
In an installed target repo, it may also apply an already-local, local-safe kit
update before returning those commands, but only when the target Git worktree is
clean. Dirty target repos report the blocked local update and keep files
untouched.

Use this when you want startup with no target writes:

```bash
kit start --no-update
```

Use this when you want to see whether a local update is available without
applying it:

```bash
kit start --update-policy check-only
```

If the update plan is clear and expected:

```bash
kit update
```

## Update Rules

`kit start` only uses the already-local kit checkout. It does not fetch from
GitHub, update the global launcher, or refresh a source checkout.

`kit start` also refuses to apply local-safe target writes when the target repo
already has dirty Git work. Use `kit update --dry-run` to inspect the available
update after you commit, park, or otherwise classify the dirty files.

Remote/global updates are explicit. A global tool update does not rewrite
target repos by itself. On macOS, it does refresh the optional installed Kit
Companion app when `/Applications/KitCompanion.app` or
`~/Applications/KitCompanion.app` exists.

Update the global cached tool:

```bash
kit update --global
```

The global update summary reports the tool version transition first and keeps
the source-ref transition as secondary provenance. When the app refresh runs,
the summary also reports the Kit Companion install path and version transition.

Preview a target update:

```bash
kit update --dry-run
```

Apply a target update:

```bash
kit update
```

Preview every registered enrolled target repo:

```bash
kit target dirty-report --json
kit update --all --dry-run
```

Import existing primary repos into the batch registry without importing old
task worktrees:

```bash
kit target import --root /Volumes/Myrtle/Code/04_Code --dry-run
kit target import --root /Volumes/Myrtle/Code/04_Code --apply
kit target list --json
kit target dirty-report --json
```

Apply updates across registered targets:

```bash
kit update --all --apply
```

Batch dry-run classifies dirty targets before update planning. Batch apply skips
dirty, missing, or no-longer-enrolled targets. Successful `kit setup` and
`kit update` runs add the target repo to the local registry. If the dry-run
reports stale missing entries, preview registry cleanup with
`kit target prune-missing --dry-run`, then apply it with
`kit target prune-missing --apply`.

Kit Companion exposes these batch maintenance writes behind explicit
confirmation in the Batch tab. The app can apply target import, prune missing
registry entries, run clean-target updates, and prune clean disposable
worktrees, but setup, install, global updates, self updates, and arbitrary
write-sidecar commands remain Terminal handoffs.

List every linked worktree for one repo before deciding what needs attention:

```bash
kit worktree list --repo /Volumes/Myrtle/MiniProjects/MiniCommand --json
```

This read-only inventory reports ordinary sibling worktrees, Codex worktrees,
detached checkouts, and kit task worktrees from Git's linked worktree registry.
It does not remove or classify worktrees as safe to delete.

Audit disposable task-worktree cleanup separately from primary repos:

```bash
kit worktree audit --root /Volumes/Myrtle/MiniProjects/MiniCommand --json
kit worktree prune --root /Volumes/Myrtle/MiniProjects/MiniCommand --dry-run
```

`--root` may be an exact Git repo root or a parent directory. Exact repo roots
include linked sibling worktrees from Git, such as
`MiniCommand-agent-worktrees/...`, while prune still removes only clean linked
worktrees under `agent-worktrees` paths.

`kit closeout-plan --json` now includes the same repo-aware audit under
`worktree_prune`. When clean disposable worktrees are removable, the closeout
next action points at the prune dry-run first and still reports dirty blocked
worktrees plus task-ledger blockers separately. Blocked closeout output also
includes `human_summary` and `blocker_explanations`, which translate raw blocker
codes into what is wrong, why Kit refuses to claim done, and how to address the
block safely.

For a supervised one-click closeout, use `closeout-fix`:

```bash
kit closeout-fix --repo /path/to/repo --json
kit closeout-fix --repo /path/to/repo --apply --jsonl
```

Preview is read-only. Apply mode launches a headless closeout agent for that
repo, writes sidecar job receipts, groups dirty work into logical commits,
prunes only eligible clean disposable worktrees, verifies final strict
closeout, and pushes the branch. Add `--no-push` for a local-only CLI run.
If the job makes partial progress but strict closeout still cannot pass, Kit
returns `result=blocked` with a durable `result.json` in the sidecar job
directory. That means the workflow ran but evidence or worktree blockers remain;
`result=failed` is reserved for supervisor/tool errors.

In Kit Companion, Guided Closeout is a dedicated write-capable app exception.
After confirmation, it runs the apply-and-push job for the selected target and
shows the resulting commits, pushed branches, receipts, pruned worktrees, and
blocker explanations. The Batch tab can run guided closeout for multiple dirty
targets with two concurrent jobs; each repo keeps its own job card and result
payload.

## Supervised Learning In Kit Companion

Learning is the fifth dashboard section. Opening it or pressing Refresh reads
typed local JSON for policy/status, counts, pending proposals, approved
decisions, histories, upstream reconciliation, and evaluation. Read-only loads
do not create sidecar state. Use Command Browser as the discovery and copy
fallback when you need the authoritative Terminal route.

Profile setup and policy changes remain Terminal-only:

```bash
kit setup --repo /path/to/repo --profile supervised-learning
```

With an enabled supervised policy, the app can prepare exactly six writes to
that repo's local Kit sidecar: event record, proposal create, decision record,
context build, thread-summary import, and upstream source-review candidate
export. Every form shows the exact command and requires final confirmation;
event record also requires explicit approval, decision record requires confirmed
human review, thread-summary import requires `--approved`, and export requires
redaction confirmation plus `public-ok` or `internal` privacy.

Thread-summary import accepts one strict, bounded, explicitly redacted local
aggregate. The app validates it, creates a private temporary copy for the
confirmed import, deletes the copy afterward, and never mines history or reads
raw transcripts. Upstream export creates only a local source-review candidate:
the app cannot self-update, update a target, push, release, execute the proposal,
or propagate it. It performs no target-repository or global Kit writes.

Cold-launch the read-only Learning view with:

```bash
open -a KitCompanion --args --open-dashboard learning
```

Malformed or unknown routes are inert. The optional app never replaces the
authoritative CLI workflow.

Review proposed replacements under `.doc-contract-kit/updates/` instead of
copying them blindly over target-owned decisions.

Use `git_worktree_state` for real Git dirt and `kit_managed_state` for kit
template/proposal state. Managed proposals need a review decision, but they are
not the same as uncommitted product-code changes.

## If You Are Lost

Use this order:

```bash
kit status
kit mode-check
kit doctor
kit closeout-plan
kit help
```

For full update detail, read [upgrade-flow.md](upgrade-flow.md).

For exact command flags, read [cli-reference.md](cli-reference.md).
