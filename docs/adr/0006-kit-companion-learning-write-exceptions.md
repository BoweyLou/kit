# ADR 0006: Kit Companion Learning Write Exceptions

## Status

Accepted

## Context

ADR 0004 keeps Kit Companion's generic command runner read-only or preview-only
and requires each app write workflow to use a dedicated allowlist. ADR 0005
defines supervised learning artifacts as opt-in, policy-gated, local sidecar
state that cannot execute recommendations or modify target/global state.

Operators need a visible Learning dashboard for review and bounded capture, but
making the generic runner accept `learn` commands would blur CLI authority,
permit route/flag drift, and risk turning local evidence into implicit action.

## Decision

Extend ADR 0004 with one dedicated typed Learning runner aligned to ADR 0005.
The generic runner must reject the complete `learn` namespace. The dedicated
runner accepts exact known routes, typed bounded fields, one absolute selected
repo, `--json`, and no `--apply`, `--global`, `--write`, `--write-sidecar`,
`--force`, positional extras, unknown flags, duplicate singleton flags, or
namespace-only commands.

Dashboard selection, cold launch with `--open-dashboard learning`, and Refresh
are read-only. Malformed or unknown cold-launch routes are inert. Profile setup
and target-owned policy changes remain Terminal-only. Command Browser remains a
discovery/copy fallback and cannot execute learning commands.

Permit exactly these six local sidecar writes:

1. Event record requires enabled policy, bounded typed input, the explicit event
   approval toggle producing `--approval-state approved --approved`, an exact
   command preview, and final confirmation.
2. Proposal create requires enabled policy, bounded typed input, existing valid
   event lineage, an exact command preview, and final confirmation.
3. Decision record requires enabled policy, an existing pending proposal, the
   human-review toggle producing `--human-review-confirmed`, an exact command
   preview, and final confirmation.
4. Context build requires enabled policy, current approved decision/proposal
   lineage, an exact command preview, and final confirmation.
5. Thread-summary import requires strict bounded redacted local JSON, explicit
   `--approved`, an exact command preview, and final confirmation. The app must
   re-encode it to a private temporary file, import only that copy, delete it,
   and never scan or mine conversation history, transcripts, feedback, runtime
   state, or network sources.
6. Upstream export requires current approved lineage, `public-ok` or `internal`
   privacy, the redaction toggle producing `--redaction-confirmed`, an exact
   command preview, and final confirmation. It creates only a local source-review
   candidate.

Serialize learning writes per repo. Bind pending confirmation to the current
repo selection. Decode successful output into route-specific read models and
reject a payload whose command, repo, policy, ownership, or write guarantees do
not match the expected contract.

## Consequences

The app can support supervised learning without becoming a general write
console. The six exceptions may create only local selected-repo sidecar
artifacts. They cannot change target files or global Kit state, execute a
recommendation, self-update, update source or a target, commit, push, release,
or propagate a candidate.

Disabled policy, invalid input, stale lineage, repo changes, malformed JSON,
unknown routes or flags, process failures, and typed payload mismatches fail
closed. Rejected attempts create no app-authorized write; partial CLI failures
remain contained to the CLI's sidecar transaction and are surfaced as errors.

Any seventh learning write, relaxation of a confirmation gate, target/global
write, automatic capture, history mining, recommendation execution, or
propagation path requires a new ADR, dedicated runner change, tests, operator
documentation, and explicit human approval.
