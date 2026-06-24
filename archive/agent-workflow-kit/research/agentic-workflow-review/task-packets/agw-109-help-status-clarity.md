# AGW-109 Task Packet: Help And Status Clarity

## Source

- Backlog item: `AGW-109`
- Implementation repo: `/Volumes/Myrtle/Code/04_Code/repo-contract-kit`
- Source repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`

## Problem

The public help surface is still close to a flat command inventory, and status
text can show global tool and target install versions without explaining which
version means what. Humans need scenario-first help and explicit version-role
language before they run setup, update, doctor, or agent automation commands.

## Scope

- Rework `kit --help`, `kit options`, and `kit help --all` around daily,
  agent/automation, and maintainer lanes.
- Keep `kit options` concise and scenario-first for humans.
- Keep advanced commands discoverable under `kit help --all`.
- Improve text `kit status` output so it distinguishes global tool checkout,
  target install metadata, prompt snapshot/source ref, and target repo version.
- Add stale or mismatch next-command guidance when target install metadata is
  missing, old, or differs from the running tool version.
- Update README/release metadata and regression tests.

## Non-Goals

- Do not redesign successful JSON payloads.
- Do not change install/update mutation behavior.
- Do not implement explicit non-interactive/agent mode, completions, or compact
  update/doctor summaries; those are later backlog items.

## Acceptance

- `kit --help` contains scenario lanes for daily, agent/automation, and
  maintainer use instead of only raw argparse inventory.
- `kit options` starts from common human scenarios and still avoids advanced
  automation inventory.
- `kit help --all` exposes the advanced agent/automation and maintainer command
  lanes, including command-map and parse-error recovery guidance.
- Text `kit status --repo <repo>` labels running tool version separately from
  target install version and target repo version.
- Text status gives a clear next command for not-installed, stale/mismatched, or
  aligned installs.
- Tests cover help/options/status text; existing JSON tests remain unchanged.

## Validation

- Add failing tests first for help/options/status text.
- Run focused tests before implementation to confirm the red state.
- After implementation, run focused tests, `make test`, `make docs-check`,
  `make docs-freshness`, `make version-check`, `make workflow-source-check`, and
  `git diff --check` in `repo-contract-kit`.
- After pushing implementation, close AGW-109 in the source backlog and run
  source `make backlog-check`, `make backlog-split-check`, and `make agent-verify`.
