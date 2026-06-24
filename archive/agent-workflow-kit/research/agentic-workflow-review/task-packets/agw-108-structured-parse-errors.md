# AGW-108 Task Packet: Structured Parse Errors

## Source

- Backlog item: `AGW-108`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Source repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`

## Problem

Default argparse failures are technically correct but noisy. Humans need likely
next commands and agents need a parseable error envelope when a command,
subcommand, flag, or enum value is wrong.

## Scope

- Add a parser/error adapter for top-level unknown commands, nested unknown
  subcommands, invalid flags, and invalid enum values.
- Include did-you-mean suggestions based on the real parser command tree and
  option choices.
- Preserve normal text-mode stderr behavior while making the text shorter and
  more actionable.
- Emit a schema-versioned JSON error envelope when `--json` appears in the
  attempted argv or `KIT_AGENT=1` is set.
- Include concise next commands and parser context in the JSON envelope without
  dumping full help.
- Update docs and release metadata because CLI failure behavior is public.

## Non-Goals

- Do not replace argparse or redesign existing successful command payloads.
- Do not add shell completions, command palette behavior, or grouped status
  summaries; those are later backlog items.
- Do not require a target git repository for parse-error reporting.

## Acceptance

- Unknown top-level command returns exit code `2`, a concise text error, and a
  nearest-command suggestion.
- Unknown nested command such as `kit target updat` suggests `target update`.
- Invalid option and invalid enum failures include the offending token and a
  likely next command or valid choices.
- JSON mode and `KIT_AGENT=1` return valid JSON on stdout with
  `schema_version`, `command: "parse-error"`, `error.kind`, `message`,
  `argv`, `suggestions`, `next_commands`, `target_repo_writes`, and
  `sidecar_writes`.
- Text failures do not dump full global help unless the user explicitly asks for
  help.
- Regression tests cover text and JSON failures.

## Validation

- Add failing tests first for text and JSON parse failures.
- Run focused CLI tests before implementation to confirm the red state.
- After implementation, run focused tests, `make test`, `make docs-check`,
  `make docs-freshness`, `make version-check`, `make workflow-source-check`, and
  `git diff --check` in `repo-contract-kit`.
- After pushing implementation, close AGW-108 in the source backlog and run
  source `make backlog-check`, `make backlog-split-check`, and `make agent-verify`.
