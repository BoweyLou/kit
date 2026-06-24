# Docs-Impact Benchmarks

This fixture suite seeds `AGW-046` and `AGW-122`: deterministic docs-impact
benchmark cases for false positives, false negatives, covered changes, explicit
`No docs needed:` style waivers, and source task-packet research handoffs.

The suite is not a replacement for `scripts/check_doc_impact.py`. The runner
loads `doc-contract.json` and calls the existing docs-impact evaluator, then
compares the result with the expectations recorded in
`docs-impact-benchmarks.json`.

## Files

- `docs-impact-benchmarks.json`: source fixture suite with case ids, changed
  files, optional no-docs declarations, expected status, expected categories,
  false-positive or false-negative intent, and packet-to-summary handoff cases
  for `research/agentic-workflow-review/task-packets/`.
- `../../scripts/run_docs_impact_benchmarks.py`: deterministic stdlib runner.
- `../../tests/test_docs_impact_benchmarks.py`: focused unit tests for the
  fixture shape, expected-output comparison, and failure reporting.

## Run

```sh
python3 scripts/run_docs_impact_benchmarks.py
python3 scripts/run_docs_impact_benchmarks.py --json
```

The runner does not inspect git state, create temporary repositories, or use the
network. It evaluates only the changed-file lists recorded in the fixture
suite, so output is stable across worktrees.
