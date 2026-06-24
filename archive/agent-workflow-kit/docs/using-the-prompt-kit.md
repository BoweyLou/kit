# Using agent-workflow-kit

This is legacy source-checkout guidance. Current workflow-source edits belong
in `repo-contract-kit/workflows/`; this page keeps historical prompt recipes and
manual-use guidance readable for archive validation and migration comparison.

The historical prompts in this checkout live under `workflows/prompts/` and can
still be used from Codex, AmpCode, Claude Code, Aider, Cline, or a manual review
session when archive context is needed. `.codex/prompts/` is the generated
native Codex projection of that legacy tree, not the live prompt source.
Current prompt, schema, adapter, and task-packet source changes start in
`repo-contract-kit/workflows/`.

For installable repo guardrails, pair this kit with
[repo-contract-kit](https://github.com/BoweyLou/repo-contract-kit).

## Working Rhythm

Use [Working Rhythm](working-rhythm.md) as the human-facing entrypoint. The
daily command vocabulary is:

1. Orient with `make agent-start` and `make kit-status`.
2. Review with `make agent-run-review AGENT=manual` or the persona prompts.
3. Scope with `make agent-task-packet`.
4. Execute approved write work with `make agent-task-prepare` in an installed
   target repo, then validate with `make agent-verify`.

## Quick Repo Review

Use this when you want a fast but useful read on a repo.

1. Run `workflows/prompts/multi-agent-repo-review.md`.
2. Dispatch these personas:
   - `workflows/prompts/personas/doc-code-delta.md`
   - `workflows/prompts/personas/ai-code-slop.md`
   - `workflows/prompts/personas/reuse-architecture.md`
   - `workflows/prompts/personas/test-behavior-risk.md`
3. Merge outputs with `workflows/prompts/review-synthesis.md`.
4. Use `workflows/prompts/fix-planner.md` only for findings you accept.

Review synthesis can record optional receipt metrics for review outcome and
effort: yield, false-positive and duplicate rates, latency, time to green,
known token/cost effort, and human review burden. These metrics calibrate the
workflow; they do not prove productivity. Interpret them beside severity,
false-positive notes, duplicate rate, human decisions, review time, and
validation quality. Unknown cost, latency, or human-burden values should be
omitted or caveated, not guessed.

For review-only local or self-hosted model passes, read
[`docs/runtime-compatibility.md`](runtime-compatibility.md) and
`workflows/prompts/policies/local-private-review.md` before choosing a model or
provider. Local models are useful for low-risk first passes, duplicate triage,
and private-context escalation decisions, but high-risk security, privacy,
compliance, data, release, production, or large-architecture findings need a
stronger reviewed path or human review. Receipts should record the actual data
boundary, model/provider expectations, capability caveats, and escalation
decision.

`doc-code-delta` treats behavior-describing comments and docstrings as
maintained documentation, but drift there is advisory by default. Open findings
need evidence from both the maintained comment/docstring and the current
implementation, tests, docs, ADR, or runtime behavior; generated/vendor,
historical, framework-convention, simplified-example, and speculative cases
should be labeled as false positives, rejected, or deferred.

## Review Maps For Large Changesets

Use `workflows/prompts/templates/review-map.md` when a diff is too broad for a
single linear review pass.

1. Start from `make context-packet` or an installed context bundle when
   available.
2. Record the diff range, task packet, receipts, and manual inspection notes in
   the source inputs.
3. Group changed files into reviewable clusters with rationale, owner or area,
   supporting context, and uncertainty.
4. Name entrypoints, public contracts, data/schema boundaries, operational
   surfaces, docs, ADRs, scripts, and tests that reviewers must inspect.
5. Route default and specialist personas from the risk hotspots, then write a
   recommended review sequence and validation evidence list.
6. Fill omissions for skipped files, unclassified paths, missing context data,
   ambiguous ownership, validation gaps, and unknowns.

If a tool needs structured output, validate against
`schemas/review-map.schema.json`. A review map is a navigation artifact. It
helps reviewers avoid generic findings, but it does not replace direct
inspection of source, tests, docs, ADRs, scripts, runtime configuration, or
receipts.

## Maintainer Queue

Use this when you want to decide what should happen next across backlog rows,
active task packets, receipts, and local readiness checks.

1. Run `workflows/prompts/maintainer-queue.md`.
2. Ground the report with `make backlog-status`, `make agent-next`, and
   `make agent-task-status` when available.
3. Classify work into `Active`, `Needs owner`, `Ready next`, and `Blocked`.
4. Convert only the selected `Ready next` item into a task packet before
   implementation.

The queue prompt is intentionally not a release, merge, credential, PR-mutation,
or thread-management command. Those actions require separate explicit
authorization and, when they become repo behavior, separate backlog work.

## Trace Evidence

Use [Codex Review Trace](codex-review-trace.md) when a handoff needs one name
for the evidence behind a run. The current source-side concept is CLI-later: it
defines how a future `codex-review trace` interface should compose session
receipts, receipt summaries, task packets, context packets or bundles,
task-status, agent-state-ledger output, and closeout or finalizer receipts.

Do not use trace language as permission to export private transcripts. Prefer
local artifact paths, receipt summaries, validation results, and explicit
omission notes. Raw transcripts require an explicit local path and a redaction
choice in any future implementation.

## Backlog To Task Packet

Use this when the input is a backlog row, issue, Keryx task, accepted review
finding, or broad human request.

1. Run `workflows/prompts/task-packet.md`.
2. Fill `workflows/prompts/templates/task-packet.md`.
3. If another tool or agent needs a machine-readable handoff, emit JSON that
   validates against `schemas/task-packet.schema.json`.
4. Include previous task state and the closeout-before-start gate:
   report sources, active tasks, unresolved blockers, dirty or stale state,
   finalizer receipt paths, blocker receipt paths, start permission, and a
   `safe-start`, `refuse-start`, or `blocker-escalation` decision.
5. Include closeout requirements before handoff: final receipt path, readiness
   check, lifecycle action, final task-status check, closeout preview, and
   dirty-state explanation.
6. Use the packet to choose the next prompt:
   - `fix-implementer.md` for approved implementation work.
   - `tdd/README.md` when behavior should be driven by tests.
   - `verification-sentinel.md` when the task is verification-only.

Do not send implementation work forward while previous task state is unresolved,
missing finalizer or blocker receipt evidence, or marked for refusal or blocker
escalation.

Task packets are the backlog surface for this kit. Do not build a backlog UI or
status app unless a target repo explicitly needs one.

### Phase Files For Large Work

Use phase files when one approved task packet is still the right scope, but the
review or implementation is too large for one fresh agent session. A phase file
is a bounded continuation artifact. It preserves what the next session needs to
know; it does not replace the task packet, widen scope, or authorize unrelated
work.

Add `phase_files` to the task-packet JSON when needed:

- `needed`: whether phase files are required.
- `reason`: why the packet cannot be executed safely in one fresh session.
- `base_path`: where phase files should live, such as a task artifact directory
  or sidecar path.
- `phases`: short ordered phase entries with `id`, `title`, `objective`,
  `allowed_scope`, `completion_evidence`, and optional `handoff_notes`.

Each phase should be independently resumable. It should name the source inputs,
allowed files, validation evidence, stop conditions, and the completion evidence
required before the next phase starts. If the work is small, leave phase files
off and keep the packet itself as the complete handoff.

## Write-Capable Task Isolation

Use this when an accepted task will edit files, especially if another agent or
human may work nearby.

1. Read `docs/worktree-per-task-runner.md`.
2. Prepare the task packet first so the scope and approval state are explicit.
3. In a target repo installed with `repo-contract-kit`, run
   `make agent-task-prepare TASK=<id>`.
4. Give the generated task packet and receipt template to the write-capable
   worker.
5. Review the task branch before staging, committing, pushing, or merging.

Do not send a write-capable worker into the main checkout when unrelated work is
already present or when parallel tasks could touch the same files.

## Full Release Gate

Use this before publishing, merging a large branch, or trusting an inherited codebase.

Run every persona in `workflows/prompts/personas/`, then synthesize:

- Documentation/code delta
- AI code slop
- Reuse and architecture
- Dead code
- Duplication
- Test and behavior risk
- Security and privacy
- API and data contracts
- Dependencies and build
- Runtime and observability
- Frontend UX, if applicable

The synthesis should produce:

- Merge blockers
- Fix-now maintenance risks
- Deferred cleanup
- Human decisions
- Not-recommended changes

## Pull Request Drift Review

For PRs, constrain reviewers to the diff first.

Brief each persona with:

```markdown
Review mode: pull-request
Scope: changed files first; inspect callers, tests, docs, and workflows only as needed.
Goal: identify behavior, docs, tests, and maintenance drift introduced by this diff.
Output: maximum 5 findings, ranked by merge risk.
```

Add full-repo inspection only when a reviewer finds evidence that the diff crosses a shared contract.

## AI Slop Cleanup Pass

Use this when a branch has too much agent-generated code or a suspiciously broad patch.

1. Run `ai-code-slop.md`.
2. Run `reuse-architecture.md` on only the files flagged by the slop reviewer.
3. Run `test-behavior-risk.md` on the accepted cleanup scope.
4. Use `fix-planner.md` to create one cleanup batch at a time.
5. Use `fix-implementer.md` for only the first batch.
6. Use `verification-sentinel.md` before moving to the next batch.

Good cleanup batches are usually:

- Remove fake fallback behavior.
- Replace ad hoc parsing with an existing structured parser.
- Collapse a one-off abstraction back into local code.
- Move duplicated validation to the existing source of truth.
- Add regression tests around behavior before simplifying.

## Codebase Learning Comments Pass

Use this when the goal is to understand the codebase better, not to change behavior.
It supports two audiences: a learning developer who may later edit code, and a
non-developer stakeholder who needs a plain-language explanation of code intent,
domain rules, data flow, and operational boundaries.

1. Run `workflows/prompts/codebase-learning-comments.md`.
2. Dispatch the documentation, ADR, code-path, comment-verifier, comment-author, and verification subagents described in that prompt.
3. Start ADR discovery from existing `agent-start`, session-start,
   context-packet or context-bundle ADR evidence, and task or operator decision
   references before scanning compact ADR-like paths manually.
4. When no ADR or decision record exists, record that absence, use README,
   docs, tests, code, config, changelog, task context, and operator
   instructions as fallback evidence, and keep unsupported architecture intent
   out of comments.
5. Choose inline comments, a separate explanation note, or a narrow mix of both.
6. Add comments only where they explain intent, invariants, non-obvious control
   flow, domain concepts, or cross-file relationships.
7. Prefer the explanation note when useful context would make source noisy,
   teach syntax, over-simplify a domain rule, or compensate for missing design
   context with evidence-backed code-path explanation.
8. Reject comments that restate the next line of code, teach general syntax,
   swap jargon for inaccurate wording, or hide uncertainty.
9. Run the verification checks recommended by the prompt to confirm source edits are comment-only and behavior-neutral.
10. Fill the session receipt's `evidence.comment_only_verification` with the
   diff scope, `scope.behavior_change=false` assertion, reviewed changed files,
   evidence commands, any behavior-safe explanation-note paths, and unresolved
   uncertainty. For a no-source explanation-note run, record that no files
   changed and set `source_files_changed=false`.

Good comment targets are usually:

- A module entrypoint that is hard to place in the wider system.
- A domain rule whose reason is not obvious from the code.
- A boundary with an external API, data format, scheduler, or framework convention.
- A branch that protects against a historical bug or operational failure.
- A compact explanation of why code deliberately avoids an easier-looking approach.
- A non-developer explanation of domain terms, data flow, external boundaries,
  state transitions, operational constraints, and surprising guardrails when
  that context is better kept out of source files.

## TDD and Executable Specs Pass

Use this when a review finding, bug fix, refactor, or feature should be backed by executable behavior.

1. Start from `workflows/prompts/tdd/README.md`.
2. Choose the prompt that matches the work:
   - `test-first-feature.md` for new behavior.
   - `regression-first-bugfix.md` for bugs.
   - `characterization-before-refactor.md` for unclear existing code.
   - `contract-test-design.md` for APIs, schemas, event payloads, generated clients, and file formats.
   - `property-and-invariant-tests.md` for parsers, ranking, scheduling, sync, reconciliation, and policy logic.
   - `test-quality-sentinel.md` before considering the change done.
3. Write or propose the failing test before production code whenever practical.
4. Implement the smallest passing change.
5. Refactor only under passing tests.

Good test-first targets are usually:

- A bug that can be reproduced as a regression test.
- A refactor that needs characterization tests before cleanup.
- A public API or data-shape change that needs contract tests.
- A domain rule that has invariants beyond a few examples.
- A risky AI-generated patch that needs executable proof before simplification.

## Dead Code Cleanup Pass

Use this when a repo has old branches, stale scripts, or abandoned features.

1. Run `dead-code.md`.
2. Run `dependencies-build.md` for package exports, scripts, and CI references.
3. Run `doc-code-delta.md` for docs that may still advertise removed features.
4. Only delete items marked `safe delete`.
5. For `likely dead` items, deprecate, quarantine, or add runtime telemetry before deletion.

## Finding Quality Gate

Reject a finding if it lacks:

- A concrete file path or command.
- A reachable behavior or maintenance risk.
- A scoped recommendation.
- A verification path.

Accept a finding when:

- The evidence is reproducible.
- The impact is specific.
- The proposed fix is smaller than the problem it solves.
- The reviewer has considered false positives such as dynamic imports, public APIs, generated files, and framework conventions.
- Comment/docstring drift has two-sided evidence and is labeled as advisory
  unless public behavior, operations, security/privacy, or likely future edits
  create concrete impact.
