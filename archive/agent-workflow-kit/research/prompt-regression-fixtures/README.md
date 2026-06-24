# Prompt Regression Fixtures

This fixture suite seeds `AGW-047`: deterministic prompt-output regression
checks for reviewer persona findings and synthesis findings.

The suite is not a model benchmark. It does not call an LLM or inspect live git
state. The runner loads small golden payloads from
`prompt-regression-fixtures.json`, reuses the payload validators from
`scripts/agent_review_run.py`, and applies narrow quality checks for evidence,
false-positive notes, low-signal nits, source-persona preservation, and
duplicate synthesis findings.

## Files

- `prompt-regression-fixtures.json`: source fixture suite with case ids, intent
  labels, payload inputs, expected pass/fail status, and expected validation or
  quality reasons.
- `../../scripts/run_prompt_regression_fixtures.py`: deterministic stdlib
  runner.
- `../../tests/test_prompt_regression_fixtures.py`: focused unit tests for the
  fixture shape, expected-output comparison, and failure reporting.

## Run

```sh
python3 scripts/run_prompt_regression_fixtures.py
python3 scripts/run_prompt_regression_fixtures.py --json
```

`make validate` also runs the text-mode fixture runner so prompt-output
regressions are covered by the normal local verification path.
