# Sidecar Retention

Kit sidecar state is local operator evidence. It is outside the target repository and is never deleted by default.

## Default Policy

- Default retention window: 90 days for routine receipts, task packets, review artifacts, feedback, and automation handoffs.
- Privacy labels: `public-ok`, `internal`, `private-local`, `sensitive-local`.
- Default label: `private-local`.
- Hosted model sharing: do not upload sidecar receipts, feedback, private context, or task packets to a hosted model unless a human explicitly approves the specific content.
- Purge behavior: `kit retention --json` only previews candidates. It does not delete files.

## Safe Archive Guidance

Archive receipts that support release decisions, migration proof, rollback decisions, or accepted findings before purging local state. Keep enough evidence to reconstruct why a task was selected, which mode was used, what validation ran, and what human approval existed.

## Purge Preview

Use `kit retention --json` to list sidecar directories, privacy labels, retention windows, and candidate counts. Review the preview manually before deleting anything with external tools.

## Supervised Learning Records

The opt-in `supervised-learning` profile keeps its policy in the target repo,
but learning events, proposals, decisions, and context belong under the
target's repository-specific local Kit sidecar. Approved events are stored as
schema-valid JSON files under `<sidecar>/learning/events/`; their default
privacy label and retention window come from the target-owned policy.

`kit learn event record` accepts only bounded explicit CLI fields and requires
both an installed enabled policy and `--approved`. It records stable IDs,
timestamps, provenance, privacy labels, outcomes, and approved supervision.
`kit learn proposal create` stores only a schema-valid pending-review proposal
under `<sidecar>/learning/proposals/` after it validates every supplied event
ID against an existing local approved event. Proposals keep stable IDs, bounded
scope/classification/recommendation fields, event lineage, privacy, and an
explicit no-execution guarantee. `kit learn decision record` requires a named
human decider, non-empty rationale, `--human-review-confirmed`, and an existing
pending proposal; it writes the decision under `<sidecar>/learning/decisions/`
and updates the linked proposal status to approved, rejected, or deferred.

Rejected, unapproved, invalid, disabled, unenrolled, invalid-evidence,
missing-proposal, non-pending-proposal, or missing-human-review attempts do not
create or update sidecar state. Event, proposal, and decision lists plus
`kit calibration` remain read-only; calibration labels its event count as
derived and caveated.

Do not move learning records into global kit state, source code, Git history,
or a hosted model by default. Do not reinterpret, migrate, or implicitly copy
the separate `kit feedback` ledger into learning events. Approved decisions are
not execution authority: they cannot write AGENTS.md, policy, target files, or
global tool state, and Kit never executes recommendations. Preserve approved
proposal and decision evidence before any later purge workflow is introduced.
