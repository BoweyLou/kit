# AGW-114 Task Packet: Shell Completions

## Source

- Backlog item: `AGW-114`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Source repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`

## Problem

HN feedback treats shell completion as core CLI discoverability. `kit` already
has a parser-backed command map, so completions should be generated from that
same source instead of copied into stale shell-specific files.

## Scope

- Add `kit completion bash|zsh|fish`.
- Generate top-level command names, nested subcommands, and flags from the
  parser-backed command map.
- Keep the command read-only and stdout-only; no shell config files should be
  written by default.
- Add command-map metadata for the completion command.
- Add README snippets for installing bash, zsh, and fish completions.
- Add regression tests that completion output tracks command-map command paths
  and common flags.

## Non-Goals

- Do not mutate `.bashrc`, `.zshrc`, fish config, or shell completion
  directories.
- Do not add a dependency on completion-generation libraries.
- Do not implement a TTY command palette in this slice.
- Do not generate full CLI reference docs in this slice.

## Acceptance

- `kit completion bash`, `kit completion zsh`, and `kit completion fish` exit
  successfully and print shell completion code.
- Generated completion output includes command-map command paths, nested
  `self`/`target` subcommands, completion shell choices, and parser flags such
  as `--repo`, `--json`, and `--no-input`.
- The command writes no target repo or sidecar files.
- `kit command-map --json` advertises `completion` as a read-only human route
  with `shell_completion_script` output.
- README documents shell-specific install snippets.

## Validation

- Add failing completion tests before implementation.
- After implementation, run focused completion and command-map tests,
  `make test`, `make docs-check`, `make docs-freshness`, `make version-check`,
  `make workflow-source-check`, and `git diff --check` in `repo-contract-kit`.
- After pushing implementation, close AGW-114 in the source backlog and run
  source `make backlog-check`, `make backlog-split-check`, `make agent-verify`,
  and `git diff --check`.
