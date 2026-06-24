# Codex Review Trace

`codex-review trace` is a source-side concept for a later local interface that
opens or exports the evidence behind an agent run.

No `codex-review trace` CLI command, Make target, installed kit behavior,
hosted service, GitHub bot, or trace database ships from this repository today.
This page defines the contract future CLI work should satisfy.

## Definition

A trace is a local evidence map for one run, task, or handoff. It answers:

- which run or task is being reviewed
- which evidence artifacts exist
- which artifacts are missing, stale, invalid, or intentionally omitted
- which validation checks support the handoff
- which privacy policy was used for any exported handoff

A trace composes existing workflow evidence. It does not replace receipts, task
packets, review maps, context packets, task status, the state ledger, or
closeout receipts. It also is not a raw transcript archive. Transcript review
can be supported by pointing a human to an explicit local transcript path, but
transcript export is never automatic.

## Evidence Surfaces

A future trace interface should gather pointers, status, validation results, and
omission reasons from existing artifacts.

| Surface | Current source | Trace role |
| --- | --- | --- |
| Session receipt | `.agent-workflows/runs/*/receipt*.json`, task receipts, and `.agent-workflows/schemas/session-receipt.schema.json` | Core run facts: mode, scope, files, commands, docs impact, tests, findings, skipped checks, and disposition. |
| Receipt summary | `make receipt-summary RECEIPT=...` and `scripts/render_session_receipt_summary.py` | Human-readable evidence digest so reviewers do not need full transcripts for normal handoff. |
| Task packet | `workflows/prompts/task-packet.md`, `schemas/task-packet.schema.json`, and packet artifacts | Declared goal, scope, protected paths, acceptance, validation, prior-task state, and closeout requirements. |
| Review map | `workflows/prompts/templates/review-map.md` and `schemas/review-map.schema.json` | Large-changeset navigation: changed-file clusters, entrypoints, contracts, risk hotspots, review sequence, validation evidence, omissions, and follow-up task-packet candidates. |
| Context packet | `make context-packet` and `scripts/build_context_packet.py` | Changed-file context, likely callers, tests, docs, ADRs, scripts, and runtime config references. |
| Context bundle | Installed `agent-context-bundle`, when available | Bounded startup or handoff snapshot that combines local state and explicit omissions. |
| Task status | `make agent-task-status` in installed repos | Active scopes, worktrees, leases, hazards, and coordination warnings. |
| Agent-state ledger | Installed `agent-state-ledger`, when available | Read-only local index of dirty state, task metadata, receipts, finalizers, automation state, blockers, and next safe commands. |
| Closeout and finalizer receipts | Installed task lifecycle, readiness, finalizer, and closeout receipts | Proof that a task reached a terminal or blocked state with linked receipt, final status, and closeout preview evidence. |

When one of these surfaces is unavailable, a trace should report the omission
instead of inventing evidence. Missing evidence is useful debugging output.

## Modes

Future CLI work should treat these as planned modes, not current behavior.

`inspect` or `open`:
List the local evidence artifacts for a selector and optionally open a local
file or directory. This mode is for the operator sitting at the machine.

`export`:
Write a local bundle containing a manifest, receipt, receipt summary, selected
packets, selected context reports, validation results, and an omission list.
The bundle stays local and should not include raw transcripts unless the
operator supplies an explicit transcript path and accepts the redaction policy.

`handoff`:
Write a privacy-redacted Markdown or JSON handoff that can be shared with
another local worker or reviewer. This should prefer receipt summaries and
artifact paths over raw command output.

`debug-missing-evidence`:
Explain why a run cannot be traced completely. The output should name missing
or invalid artifacts, likely stale state, and the next local command or receipt
needed before handoff.

## Privacy And Local-Only Boundary

Trace handling is local-first and privacy-preserving by default.

- Do not automatically export private Codex transcripts.
- Do not scan machine-local Codex history, browser state, accounts, cookies, or
  credentials unless the operator passes an explicit local artifact path for a
  future implementation to inspect.
- Do not upload trace bundles, summaries, transcripts, receipts, or command
  output to a remote service.
- Do not call the GitHub API, hosted models, browser automation, or account
  mutation flows as part of trace generation.
- Do not mutate task metadata, receipts, branches, PRs, issues, accounts, or
  sidecar state. Trace is an evidence reader and exporter, not a lifecycle
  command.
- Redact or omit credentials, tokens, cookies, account identifiers, private
  URLs, private local paths, secrets, and sensitive command output.
- For local inspection, absolute paths can be useful. For handoff or export,
  prefer repo-relative paths, artifact labels, hashes, and explicit omission
  notes when paths reveal private machine details.
- Long command output should be summarized unless the operator explicitly
  marks it safe and necessary for the local handoff.

If redaction cannot make an artifact safe for the selected mode, the trace
should omit it and record why.

## Future CLI Contract Sketch

This section is intentionally a sketch for later implementation work. It does
not document shipped flags.

Potential selectors:

- task id, such as `AGW-029`
- run id from a session receipt or startup packet
- receipt path
- task packet path
- review-map path
- sidecar task directory
- explicit context-packet or context-bundle path
- explicit state-ledger snapshot path

Potential options:

- mode: `inspect`, `export`, `handoff`, or `debug-missing-evidence`
- output path for a local bundle or handoff file
- redaction profile, such as local-inspect, handoff, or strict
- optional explicit transcript path
- JSON and Markdown output format selectors
- strict validation mode that refuses incomplete evidence

Expected outputs:

- a trace manifest with selector, generated time, local-only status, redaction
  profile, included artifacts, omitted artifacts, validation results, and next
  local commands
- a Markdown summary suitable for a reviewer
- an optional local export directory or archive
- a refusal report when the request crosses privacy, mutation, or completeness
  boundaries

Refusal cases:

- remote upload, hosted processing, GitHub API mutation, browser account
  mutation, or credential use is requested
- raw transcript export is requested without an explicit local transcript path
  and an explicit redaction choice
- the selector is ambiguous and several runs or tasks match
- required artifacts are missing or fail validation in a mode that claims
  completeness
- the requested output path would overwrite unrelated files or leave the repo
  boundary without explicit operator approval
- the bundle would include secrets or sensitive content that cannot be safely
  redacted for the selected mode
- the request asks trace generation to finish, close, clean up, or mutate task
  lifecycle state

Validation expectations:

- validate session receipts with the existing strict receipt validator
- render receipt summaries from the receipt being traced
- validate task packets against the task-packet schema when a packet is present
- record task-status and state-ledger snapshots as local read-only evidence
  instead of treating them as commands to change state
- confirm closeout or finalizer receipts before claiming a task is terminal
- include omission reasons for unavailable, stale, invalid, or intentionally
  redacted evidence
- verify that any exported bundle contains a manifest, redaction policy,
  validation report, and no automatic transcript copy

## Ownership

The concept belongs in `agent-workflow-kit` because it defines how workflow
evidence should compose. A shipped installed command would belong in
`repo-contract-kit` as later work because that repo owns target-repo CLI and
Make behavior.

Until that later work exists, agents should describe trace evidence by naming
the existing artifacts directly: session receipt, receipt summary, task packet,
review map, context packet or context bundle, task status, state ledger, and
finalizer or closeout receipt.
