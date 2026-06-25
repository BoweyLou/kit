# Repo Boundary

`kit` is the install and target-repo governance layer. Its public
CLI command is `kit`. Target-repo operators should use `kit` only; they should
not need to understand or clone a separate workflow-source checkout.

For the operator-facing stack map and change-routing table, read
[`docs/agent-workflow-stack.md`](agent-workflow-stack.md).

## Ownership

`kit` owns:

- the global cURL installer and `kit` CLI
- setup/status/update/doctor flows
- installer presets, profiles, update, and migration behavior
- target-repo managed files such as `AGENTS.md`, `REVIEW.md`,
  `.agent-workflows/`, `.codex/prompts/`, `.doc-contract-kit/`, and the
  kit-owned make target fragment
- canonical workflow source under `workflows/`, including prompts, personas,
  policies, TDD prompts, research prompts, schemas, and adapter definitions
- docs-contract checks, instruction linting, receipt verification, versioning
  profile, local review runners, and optional CI/PR/runtime adapters

The former `agent-workflow-kit`/`Codex_CodeReview` source checkout is now a
legacy migration source. It can remain readable for history, but new prompt and
schema source edits start in `kit/workflows/`.

## Working Rule

For any AGW backlog item, first decide whether the change is source-facing,
install-facing, or target-facing. Target-facing work must preserve the
single-product operator path. Source-facing workflow edits must refresh the
generated target templates before they are considered done.

Use this routing rule:

- prompt, persona, schema, synthesis, TDD, research, or adapter-source changes
  start in `workflows/`
- installer, managed-template, target command, update, manifest, or docs-contract
  changes start in `kit`
- target-repo operator confusion usually starts in this repo's CLI, docs, and
  templates, then checks whether `workflows/` source also needs clarification
- release pairing stays explicit through install receipts and
  `.doc-contract-kit/manifest.json`

After changing `workflows/`, run:

```bash
make workflow-source-export
make workflow-source-check
```

The target repo owns the root `Makefile`. `kit` owns the installed
`.doc-contract-kit/make/repo-contract.mk` fragment. Updates may migrate a clean
old kit-managed root `Makefile` to a bridge, but customized target Makefiles are
preserved and receive merge guidance under `.doc-contract-kit/updates/`.
