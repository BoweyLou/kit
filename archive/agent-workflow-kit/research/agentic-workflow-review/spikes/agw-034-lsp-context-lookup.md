# AGW-034 LSP Context Lookup Spike

Date: 2026-06-16

Status: complete spike, no shipped runner behavior.

## Question

Should the local review runner grow LSP-backed definition and reference lookup
for large-repo reviews, and if so where should it compose with the existing
context-packet, review-map, trace, and read-only runner surfaces?

## Recommendation

Defer implementation from AGW-034, but create a follow-on backlog item to build
an optional local-only LSP enrichment artifact after fixture coverage exists.

This is a build-later decision, not a no-go. LSP lookup is useful when a repo
already has a working language server and the review needs definitions,
references, or symbol summaries that deterministic text matching cannot
provide. It should not replace the deterministic context packet or review map,
and it should never become a required precondition for review.

The first implementation should be artifact-only:

- read-only
- local-only
- no auto-install
- no background daemon requirement
- no remote indexing
- best-effort per language
- explicit omissions for missing servers, unsupported files, generated/vendor
  exclusions, timeouts, partial results, and truncated output

## Source Evidence

Internet access was unnecessary for this spike. The recommendation is grounded
in the checked-out source and existing research records; no new external URLs
were consulted.

Local evidence:

- `research/agentic-workflow-review/backlog.csv` records `AGW-032` as complete:
  `scripts/build_context_packet.py` emits changed files plus likely callers,
  tests, related docs, ADRs, scripts, runtime configs, and guidance.
- `scripts/build_context_packet.py` builds context deterministically from git
  changed files, repo text files, bounded file sizes, symbol/path terms, and
  fixed buckets: `likely_callers`, `likely_tests`, `related_docs`, `adrs`,
  `runtime_configs`, and `scripts`.
- `research/agentic-workflow-review/task-packets/agw-033-review-map-artifact.md`
  explicitly protected AGW-034 LSP/codegraph lookup and scoped AGW-033 to a
  Markdown/JSON navigation artifact.
- `workflows/prompts/templates/review-map.md` starts from `make
  context-packet` or an installed context bundle, records source inputs, groups
  changed-file clusters, names entrypoints/contracts, and requires omissions
  for missing or incomplete context data.
- `schemas/review-map.schema.json` makes omissions and follow-up task-packet
  candidates first-class fields instead of optional prose.
- `docs/codex-review-trace.md` defines trace as a local evidence map that
  composes receipts, task packets, review maps, context packets, task status,
  state ledger, and closeout receipts. It refuses hosted processing, GitHub API
  mutation, automatic transcript export, and lifecycle mutation.
- `docs/harness-engineering.md` frames context packets and review maps as
  harness components for context relevance, with token economy, omissions,
  permissions, receipts, and local verification as quality gates.
- `scripts/agent_review_run.py` is currently a read-only runner: it loads the
  latest startup packet, selected personas, and permission policy; writes prompt
  and JSON artifacts under `.agent-workflows/runs/`; executes manual or Amp
  review modes; validates JSON; builds a receipt; and fails if git status
  changes during a read-only run.
- `research/agentic-workflow-review/source_findings.json` records the original
  context-retrieval gap as definitions, usages, tests, docs, ADRs, runtime
  configs, and ownership context, with Sourcebot and mrge.io as examples, but it
  predates the completed AGW-032 and AGW-033 local artifacts.

## Approach Comparison

| Approach | Fit | Strengths | Weaknesses | Go / defer trigger |
| --- | --- | --- | --- | --- |
| Deterministic context packet plus review-map fallback | Required baseline | Works in any git repo, no installs, stable JSON/Markdown, transparent omissions, low latency, easy to validate | Text matching can miss dynamic references, aliases, generated entrypoints, monorepo ownership, and cross-language definitions | Keep as required fallback for every repo and every language. Use whenever LSP is absent, slow, ambiguous, or unsupported. |
| Local LSP definition/reference lookup | Optional follow-on | Can return definitions, references/usages, hover/type summaries, and language-aware symbol context without broad file stuffing | Language servers may be missing, slow, stateful, workspace-sensitive, or incomplete; results vary by language and config; dynamic languages remain partial | Build later if implemented as best-effort artifact generation with no auto-install, hard timeouts, and omission fields. Do not gate reviews on success. |
| Heavier codegraph or search indexing | Defer | Better for whole-repo call graph, ownership, cross-language search, dependency edges, and repeated large reviews | Higher setup cost, cache invalidation, storage growth, generated/vendor noise, privacy risk if remote, and more maintenance than the current harness needs | No-go for AGW-034. Reconsider only after LSP artifacts prove useful and a separate task defines local-only indexing, retention, and invalidation. |

## Later Architecture Sketch

Add a source-side design and then an installed runner artifact in a later packet.
AGW-034 ships only this note.

Inputs:

- changed files from git, explicit scope, task packet, or review-map source
  inputs
- existing context packet JSON/Markdown
- existing review-map artifact, when present
- optional explicit symbol focus list from a finding, reviewer question, or
  task packet
- ignore rules from git, deterministic generated/vendor exclusions, and future
  repo-local config

Outputs:

- definitions for changed symbols
- references/usages grouped by file and symbol
- optional hover/type/signature summaries when the server returns them
- source files inspected and omitted
- unsupported-language records
- timeouts, truncation, missing-server records, and confidence notes
- suggested review-map supporting-context entries

Artifact shape:

```json
{
  "schema_version": 1,
  "artifact": {
    "kind": "lsp_context_lookup",
    "repo": ".",
    "generated_at": "2026-06-16T00:00:00Z",
    "local_only": true,
    "network_used": false
  },
  "inputs": {
    "diff_range": "working-tree",
    "changed_files": ["path/to/file.py"],
    "context_packet": {"status": "available", "reference": "path/to/context.json"},
    "review_map": {"status": "missing", "reference": null},
    "task_packet": {"status": "available", "reference": "research/.../packet.md"}
  },
  "language_runs": [
    {
      "language": "python",
      "server": "pyright-or-pylsp-if-present",
      "status": "complete",
      "files_considered": ["path/to/file.py"],
      "symbols": [
        {
          "name": "SymbolName",
          "kind": "function",
          "definitions": [{"path": "path/to/file.py", "line": 10}],
          "references": [{"path": "path/to/caller.py", "line": 24}],
          "summary": "bounded local hover or signature text",
          "confidence": "medium"
        }
      ],
      "omissions": []
    }
  ],
  "omissions": [
    {
      "item": "vendor/",
      "reason": "generated_or_vendor_exclusion",
      "residual_risk": "references inside vendored code were not inspected"
    }
  ],
  "limits": {
    "timeout_seconds_total": 20,
    "timeout_seconds_per_language": 8,
    "max_symbols": 25,
    "max_references_per_symbol": 20,
    "max_output_tokens_hint": 3000
  }
}
```

Runner composition:

- keep `scripts/agent_review_run.py` unchanged until a later accepted task
- later runner flow should read an existing LSP artifact path just like it reads
  context packets, review maps, receipts, and permission profiles
- artifact generation should happen before persona prompts and be referenced in
  review-map `supporting_context`, `inspection_plan`, or `omissions_uncertainty`
- manual mode should still work when no LSP artifact exists
- Amp or other executed review modes should receive the artifact path and
  omission summary, not raw unbounded symbol dumps

Sidecar and cache policy:

- write artifacts under ignored local run/task sidecars, not source directories,
  unless a task explicitly asks for a checked-in fixture
- cache only local normalized results keyed by repo root, HEAD or dirty-state
  hash, language server identity, workspace config hash, and changed-file list
- expire cache entries aggressively when lockfiles, tsconfig, pyproject,
  go.mod, Cargo.toml, or language-server version changes
- never cache private source outside the repo sidecar; cache paths and bounded
  snippets only when needed for review evidence
- record cache hits as evidence and stale-cache refusals as omissions

Token and resource caps:

- default total wall timeout: 20 seconds
- default per-language timeout: 8 seconds
- default per-file timeout: 2 seconds
- maximum changed files passed to LSP: 40 before requiring a review-map cluster
  or explicit narrowed scope
- maximum symbols: 25
- maximum references per symbol: 20
- maximum snippet lines per definition/reference: 3
- maximum artifact hint for prompts: 3000 tokens, with full JSON available by
  local path

Generated/vendor exclusions:

- exclude `.git`, `.agent-workflows`, `node_modules`, `dist`, `build`,
  `coverage`, `vendor`, `__pycache__`, generated adapter outputs, generated
  lockfile-only churn, and large files by default
- report exclusions in `omissions`
- allow later explicit local config to include a normally excluded path only
  when a task packet names it in scope

Unsupported-language and omission behavior:

- missing language server: omit with `status: missing-server`; continue review
- unsupported extension: omit with `status: unsupported-language`; continue
- monorepo workspace ambiguity: omit or split by detected project root; never
  guess a global root silently
- generated/vendor-only changes: prefer deterministic context packet and docs
  checks; do not run LSP unless explicitly scoped
- timeout or partial result: include partial evidence with `status: timed-out`
  and a residual-risk note
- remote-index request: refuse and point to local-only policy
- background daemon requirement: refuse unless the daemon is already running as
  a user-controlled local tool and the later task packet permits reuse

Privacy and permission boundary:

- no uploads, remote indexing, hosted model calls, GitHub API calls, account
  credentials, package-manager installs, or telemetry
- no file writes outside ignored local sidecars or explicit fixture paths
- no source mutation, formatting, dependency install, language-server install,
  branch mutation, PR mutation, or lifecycle mutation
- absolute paths may appear in local-only artifacts, but handoff/export should
  prefer repo-relative paths and omission notes

## Language And Tool Availability

The later implementation should detect already available tools and skip cleanly.
It must not install anything during review.

| Repo language | Candidate local server if already installed | Probe shape | Expected behavior when unavailable |
| --- | --- | --- | --- |
| Python | `pyright`, `basedpyright`, or `pylsp` | detect executable and project config such as `pyproject.toml`, `setup.cfg`, or `requirements.txt` | fall back to context packet; record missing server and dynamic-language confidence limits |
| TypeScript/JavaScript | `typescript-language-server`, `tsserver`, or editor-provided TypeScript server | detect executable plus `tsconfig.json`, `jsconfig.json`, or `package.json` | fall back to context packet; record missing server or workspace-config ambiguity |
| Go | `gopls` | detect executable plus `go.mod` or package root | fall back to context packet; record missing server or module-root ambiguity |
| Rust | `rust-analyzer` | detect executable plus `Cargo.toml` workspace root | fall back to context packet; record missing server or workspace-root ambiguity |
| Unknown or unsupported | none | classify by extension and known project files | record unsupported-language omissions and continue deterministic review |

## Later Test Plan

Add tests only in a later implementation packet.

- fixture repo: small Python project with one changed function, one caller, one
  test, and expected definition/reference JSON
- fixture repo: TypeScript project with `tsconfig.json`, changed exported
  symbol, consumer file, and omitted generated directory
- fixture repo: Go module with package references and explicit module-root
  detection
- fixture repo: Rust crate with workspace root and reference cap behavior
- fixture repo: unsupported language or no language server, expecting clean
  omission records and context-packet fallback
- golden artifact tests for stable JSON fields, omission shape, token caps,
  timeout markers, generated/vendor exclusions, and no network fields
- runner composition tests proving a later review runner can include an LSP
  artifact path without mutating source and without failing when the artifact is
  missing
- privacy tests proving remote URLs, installs, and account credentials are
  refused or omitted

## Follow-On Backlog Shape

Recommended new packet title:

`Add optional local LSP context artifact generation for review handoff`

Likely owner: `agent-workflow-kit` for source concept, schema, prompt guidance,
and fixtures; companion `repo-contract-kit` work only if an installed command or
Make target is later accepted.

Likely scope:

- source-side JSON schema for `lsp_context_lookup`
- fixture repos or fixture folders with golden artifacts
- prompt guidance that consumes an LSP artifact after context packets and
  review maps
- no installed target-repo command until artifact behavior is proven
- no auto-install, no remote indexing, no codegraph service

Acceptance:

- artifact validates against a schema
- missing language servers and unsupported languages produce omissions, not
  failures
- deterministic context packet remains the fallback
- review-map guidance can reference the artifact in supporting context and
  omissions
- privacy/local-only boundaries are tested
- token/time caps are enforced and reported

Stop conditions:

- implementation requires package installs, background daemon management,
  remote search, credentials, or hosted services
- fixture coverage cannot keep output deterministic enough for reviews
- LSP results are too noisy to improve finding quality beyond the existing
  context packet and review map

## Closeout

AGW-034 should close as a completed spike note. No command, Make target, runner
integration, LSP client, codegraph indexer, semantic search service, prompt,
schema, test, version, changelog, or repo-contract-kit change is included in
this task.
