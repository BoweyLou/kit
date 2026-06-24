# AGW-126 Task Packet: Docs And Release Metadata Surfaces

## Source

- Backlog item: `AGW-126`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Implementation commit: `69810e4`
- Released version: `repo-contract-kit` `0.6.24`
- Status: `done`

## Problem

Implementation task packets could say that docs or release metadata were needed
without naming the exact docs, generated references, schemas, changelog, version,
or validation commands that satisfy the repo-contract-kit documentation
contract.

## Scope

- Extend task-packet schema and generators with explicit docs-impact fields for
  documentation surfaces, release metadata, generated docs, contract references,
  and docs validation commands.
- Add task-packet CLI overrides for those fields on direct and backlog-derived
  packet scaffolds.
- Add default docs/release surfaces to direct, backlog, and task-worktree
  packets.
- Update the task-packet prompt/template and exported Codex adapters so vague
  docs requirements are rejected before implementation handoff.
- Refresh generated CLI reference docs and operator/planning docs.
- Add regression coverage for direct, backlog, task-prepare, prompt, template,
  and schema contract paths.

## Non-Goals

- Do not change docs-impact classification rules.
- Do not require every task to edit every default documentation surface.
- Do not make task packets mutate docs, changelog, version files, or generated
  docs automatically.

## Validation

- `python3 -m unittest tests.test_repo_contract_kit_cli.RepoContractKitCliTests.test_task_packet_emits_machine_readable_scaffold tests.test_repo_contract_kit_cli.RepoContractKitCliTests.test_task_packet_from_backlog_prefills_selected_item tests.test_agent_task_prepare.AgentTaskPrepareTests.test_prepare_creates_sibling_worktree_and_local_task_artifacts tests.test_v1_consolidation.Version1ConsolidationTests.test_task_packet_contract_rejects_vague_docs_release_requirements`
- `python3 -m unittest tests.test_repo_contract_kit_cli tests.test_agent_task_prepare tests.test_install tests.test_v1_consolidation`
- `make workflow-source-check`
- `make docs-freshness`
- `make docs-check`
- `make version-check`
- `git diff --check`
- `make test`

## Closeout Evidence

- `repo-contract-kit` commit `69810e4` releases version `0.6.24`.
- Task-packet schema copies now require `documentation_surfaces`,
  `release_metadata`, `generated_docs`, `contract_references`, and
  `verification_commands` under `docs_impact`.
- Direct and backlog task-packet CLI scaffolds accept `--docs-surface`,
  `--release-metadata`, `--generated-doc`, `--contract-reference`, and
  `--docs-validation-command`.
- Task-worktree packets include the same default docs/release metadata fields.
- Full repo-contract-kit validation passed with `300` tests.
