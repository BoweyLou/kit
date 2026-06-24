# AGW-122 Task Packet: Source Task-Packet Docs Coverage

## Source

- Backlog item: `AGW-122`
- Source repo: `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview`
- Status: `done`

## Problem

New task packets under `research/agentic-workflow-review/task-packets/` are
research backlog state, but a packet-only working tree can fail docs-impact
until the summary or backlog narrative is updated. Agents need the handoff rule
recorded in the research area and covered by deterministic fixtures, not only
remembered during closeout.

## Scope

- Document the packet-to-summary handoff rule in
  `research/agentic-workflow-review/summary.md`.
- Require packet additions or updates to pair with a summary/current-status
  update, or an explicit `No docs needed: <reason>` declaration when no
  research state changed.
- Prove the rule with docs-impact benchmark fixtures:
  - task packet only fails the research docs category
  - task packet plus summary passes
  - explicit no-docs-needed waiver passes while exposing the missing category
- Add focused unit coverage that keeps those benchmark cases present.

## Non-Goals

- Do not redesign the docs-impact evaluator.
- Do not make every historical packet appear individually in the summary.
- Do not add a new source-repo command or installed target-repo behavior.

## Validation

- `python3 -m unittest tests.test_docs_impact_benchmarks`
- `python3 scripts/run_docs_impact_benchmarks.py`
- `python3 scripts/check_doc_impact.py --working-tree`
- `make docs-check`
- `make backlog-check && make backlog-split-check`
- `make agent-verify`
- `git diff --check`

## Closeout Evidence

- Added `DIB-006`, `DIB-007`, and `DIB-008` docs-impact benchmark cases for
  source task-packet research handoffs.
- Added focused test coverage for the packet-only, packet-plus-summary, and
  explicit-waiver fixture cases.
- Added the research summary rule requiring same-change summary/current-status
  coverage or an explicit no-docs-needed declaration for archival packet-only
  edits.
