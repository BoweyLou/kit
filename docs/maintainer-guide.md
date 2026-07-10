# Maintainer Guide

Use this page when changing kit itself.

## Ownership Map

| Area | Owns |
| --- | --- |
| `install.sh` | Global launcher installation and cached checkout setup. |
| `scripts/` | CLI, install/update logic, checks, reports, and helpers. |
| `templates/` | Files installed into target repos. |
| `workflows/` | Canonical prompt, persona, research, TDD, synthesis, and schema source. |
| `docs/` | Human, agent, maintainer, rollout, upgrade, and generated command docs. |
| `archive/agent-workflow-kit/` | Read-only legacy source and migration evidence. |

Do not put normal source work in `archive/agent-workflow-kit/`.

## Common Maintainer Checks

```bash
make docs-check
make docs-freshness
make workflow-source-check
make version-check
make test
```

Use a focused test first when the change is narrow, then broaden to `make test`
before committing behavior changes.

## Workflow Source Changes

When changing `workflows/` source:

```bash
make workflow-source-export
make workflow-source-check
make docs-freshness
```

Then run the relevant install/update tests so generated target surfaces are
covered.

### Supervised learning records

The `supervised-learning` profile is opt-in. Keep its initial target policy at
`.agent-workflows/learning-policy.json` target-owned, while the seven learning
schemas remain canonical under `workflows/schemas/` and mirrored into
`templates/common/` for installation. After changing a learning schema, run
`make workflow-source-export`, then verify the profile installer and
`kit learn status --repo <temp-target> --json` with an isolated XDG state
directory. Phase 2 requires an isolated-XDG temporary committed target CLI e2e
that proves the policy gate, rejected and unapproved no-write paths, an
approved `kit learn event record --approved`, read-only `kit learn event list`,
and the caveated derived event count in `kit calibration`.

Phase 3 requires that same isolated-XDG committed-target CLI e2e to prove:
profile installation; an approved event; a proposal from existing valid event
IDs; rejected invalid evidence without sidecar initialization; the negative
human-review gate; an explicit named-human decision; read-only proposal and
decision lists; and unchanged target contents plus global target registry.
Proposal and decision schemas must retain stable IDs, lineage, privacy,
bounded explicit CLI fields, and the no-execution guarantee. Do not add
task-packet or receipt linkage in this phase.

Phase 4 requires an isolated-XDG committed-target CLI e2e after the Phase 3
flow. It must prove that `kit learn context build` accepts only an existing
schema-valid approved decision with a currently valid approved linked proposal,
and writes only explicitly constructed/redacted guidance to the sidecar. The
context must carry stable context ID, decision/proposal lineage, classification,
scope, recommended change, privacy label, retention expiry, and the
no-execution guarantee; it must exclude raw event/evidence/feedback/conversation
content. Assert `kit learn context list` is read-only, the bundle includes only
a low deterministic cap of valid approved-learning context marked as
sidecar-only guidance rather than target instructions, and stale/hand-crafted
lineage is skipped with a warning. Extend the same e2e through
`kit task-packet --learning-decision <dec-id> --write-sidecar`, including
rejected/deferred/missing/invalid decision negatives that fail before packet
sidecar creation. Preserve target and enrolled-target registry bytes; do not
alter receipt mechanics or target task files. Run `kit retention --json` to
cover learning counts and expiry preview only—there is no deletion command.

Phase 5 requires an isolated-XDG temporary committed-target CLI e2e after the
Phase 4 flow. It must prove strict redacted summary input, active policy plus
`--approved`, one imported `thread-summary-import` event, and no-write
negatives for absent approval, redaction false, unsupported/raw fields, and
oversized input. Continue through an approved proposal/decision and a
redaction-confirmed `public-ok` or `internal` upstream export. Assert the
candidate excludes raw summary text, event IDs, evidence/context, and target
paths; preserve target and registry bytes. List, reconcile, and evaluate are
read-only. Reconcile must mark revalidation when the source baseline is
advanced, while a stale or tampered candidate is skipped after revalidating
current decision/proposal lineage. `scripts/mine_codex_threads.py` is local
source research only: do not add it to installer `CORE_SCRIPTS`, the CLI, or a
runtime dependency.

Exported candidates are review inputs only. Document and preserve the normal
source task, commit, test, and release path; only then may a human run `kit
self update` and a guarded target update or reconcile. Never automate that
propagation.

Do not add `supervised-learning` to a default or named preset without an
explicit approved rollout decision. Event records are bounded, explicit CLI
input only: do not repurpose `kit feedback`, mine threads, harvest
conversations, inject context, add network calls, or add global writes.
Proposal and decision commands remain recommendation-only sidecar records.
Approved-learning context remains bounded sidecar-only guidance, not target
instructions. An approved decision must not be treated as permission to modify
AGENTS.md, policy files, target files, or global state, and Kit must never
execute its recommendation.

## CLI Or Installer Changes

When changing public command behavior, install/update behavior, schemas,
profiles, generated docs, privacy/security policy, or version metadata:

```bash
make docs-freshness
make version-check
make test
```

Update `CHANGELOG.md` and `VERSION` when the change is part of a release scope.
For docs-only reshaping, a version bump is not required unless the published
operator contract changes.

Use `kit start --json` in this source checkout before implementation. It should
report `repo_role: kit-source` and a `maintainer-source` journey, then point to
the maintainer checks rather than target enrollment.

`kit start` may apply local-safe managed-file updates only in installed target
repos. In this source checkout it must stay a maintainer route and use explicit
release checks (`make docs-freshness`, `make workflow-source-check`,
`make version-check`, `make test`) instead of treating the source tree like a
target install.

## Codex Thread Mining

Mine local Codex thread history into a redacted aggregate CLI journey report:

```bash
python3 scripts/mine_codex_threads.py --report docs/cli-journey-research.md
```

Raw and intermediate artifacts stay under local state:
`${XDG_STATE_HOME:-~/.local/state}/repo-contract-kit/thread-mining/`.
The miner writes local artifacts with private permissions and `--json` prints
aggregate output by default. Use `--include-observations` only for local manual
audits. Use `--kit-related --current-kit-era` for the current kit-specific
slice, or `--since` and `--cwd-prefix` for narrower local research.

## Documentation Shape

Keep `README.md` as the short front door.

Put detail here instead:

- capability inventory: [capabilities.md](capabilities.md)
- human operation: [human-guide.md](human-guide.md)
- agent operation: [agent-guide.md](agent-guide.md)
- command flags and JSON contracts: [cli-reference.md](cli-reference.md)
- CLI/function refinement review: [cli-function-review.md](cli-function-review.md)
- Codex thread journey research: [cli-journey-research.md](cli-journey-research.md)
- update procedure: [upgrade-flow.md](upgrade-flow.md)
- source ownership: [agent-workflow-stack.md](agent-workflow-stack.md)
- v1/archive/rollback policy: [version-1-consolidation.md](version-1-consolidation.md)

## Release Boundary

Kit has one public repository, one installer, one CLI, and one
`VERSION`/`CHANGELOG.md` stream. The old `agent-workflow-kit` and
`repo-contract-kit` remotes are legacy/private/deprecated sources.

Do not create a second normal workflow-source repository or make target repos
clone workflow source at runtime.
