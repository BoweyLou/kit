# AGW-110 Task Packet: Non-Interactive And Agent Mode

## Source

- Backlog item: `AGW-110`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Source repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`

## Problem

`kit` already avoids writes by default in many paths, but the non-interactive
contract is implicit in TTY checks. Scripts and agents need explicit `--no-input`
and `KIT_AGENT=1` behavior so help, status, and parse-error paths never surprise
them with prompts or prose-only recovery.

## Scope

- Add a global `--no-input` flag.
- Treat `KIT_AGENT=1` as non-interactive mode and parse-error JSON mode.
- Surface `non_interactive` and `agent_mode` booleans in relevant JSON payloads
  without changing successful command payload semantics beyond metadata.
- Make no-arg `kit` render the guide non-interactively when `--no-input` or
  `KIT_AGENT=1` is set, even under a TTY.
- Keep help/status/error paths non-interactive and document stdout/stderr rules.
- Add regression tests for non-TTY, TTY-simulated no-input, and agent mode.

## Non-Goals

- Do not change install/update mutation behavior.
- Do not add shell completions or command palette behavior.
- Do not redesign every JSON schema; add minimal compatibility metadata only.

## Acceptance

- `kit --no-input` renders the guide and exits `0` without prompting under a
  simulated TTY.
- `KIT_AGENT=1 kit` renders a non-interactive guide and exits `0`.
- `KIT_AGENT=1 kit statuz` returns the existing parse-error JSON envelope.
- `kit status --json` includes `non_interactive` and `agent_mode` metadata.
- `kit --no-input status --json` and `KIT_AGENT=1 kit status --json` reflect the
  chosen mode in JSON.
- README/release notes document the non-interactive contract.

## Validation

- Add failing tests first for the mode contract.
- Run focused tests before implementation to confirm the red state.
- After implementation, run focused tests, `make test`, `make docs-check`,
  `make docs-freshness`, `make version-check`, `make workflow-source-check`, and
  `git diff --check` in `repo-contract-kit`.
- After pushing implementation, close AGW-110 in the source backlog and run
  source `make backlog-check`, `make backlog-split-check`, and `make agent-verify`.
