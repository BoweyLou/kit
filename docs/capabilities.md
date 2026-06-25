# Capabilities

This page is the inventory that used to make the README too dense.

## Core Contract

Kit helps a repository answer four questions:

1. What changed?
2. Which docs, contracts, or release metadata are affected?
3. Which local checks prove the change?
4. What can an agent safely do next without overwriting repo-owned work?

## Installed Guardrails

Depending on preset and profiles, kit can install:

- `AGENTS.md` and `REVIEW.md` route maps
- documentation impact and documentation freshness checks
- local Make targets for startup, review, task packets, verification, and
  update status
- `.agent-workflows/` schemas, policies, receipts, instruction budgets, task
  metadata, and sidecar routing
- `.doc-contract-kit/` install receipts, managed-file manifests, update
  reports, and proposed replacements
- optional prompt packs for review, learning comments, TDD, and local agents
- optional runtime adapters for Claude Code and GitHub Copilot
- optional private local context templates under ignored `.agent-context/`
- optional docs-as-tests assertions for local documentation claims
- optional target-owned `VERSION`, `CHANGELOG.md`, and versioning docs

## CLI Capabilities

The CLI covers:

- setup and target enrollment
- status and drift reporting
- safe managed updates and dry-run plans
- mode selection: `lite`, `standard`, `release-gated`
- docs impact and docs explanation
- instruction hygiene and instruction-diet audits
- task packet scaffolding
- verification checks
- branch/readiness evidence
- automation handoff evidence
- sidecar initialization, retention preview, and guarded self-heal
- command metadata, completions, command palette, and generated CLI reference

Use [cli-reference.md](cli-reference.md) or `kit command-map --json` for exact
flags and schemas.

## Presets

| Preset | Use when |
| --- | --- |
| `lite` | You want a short docs-contract and low-risk local workflow with escalation. |
| `minimal` | You only want the documentation contract. |
| `learning` | You want review and learning-comment prompt surfaces. |
| `test-first` | You want TDD/executable-spec prompts and test-first docs. |
| `agentic` | You want the full local-first agent workflow harness. |

Optional profiles add stack-specific or privacy-specific surfaces without
changing the core preset story.

## Safety Model

Kit updates are managed-file updates, not repo resets.

- target-owned files stay target-owned
- customized managed files are preserved
- proposed replacements are written under `.doc-contract-kit/updates/`
- JSON output reports whether target repo writes or sidecar writes occurred
- read-only commands should report `target_repo_writes.performed: false`

When in doubt, run:

```bash
kit status --json
kit update --dry-run --json
kit command-map --json
```
