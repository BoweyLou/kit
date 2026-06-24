# Agentic Regression Fixtures

This folder seeds `AGW-056`: a regression fixture suite for agent workflow
changes. The goal is to catch prompt, schema, permission, and evidence
regressions before they show up in real coding sessions.

## Files

- `agentic-regression-seed.json`: initial fixtures derived from the X, GitHub,
  Hacker News, and findings reports in this folder.
- `../../schemas/agentic-regression-fixture.schema.json`: JSON schema for the
  fixture suite format.

## Fixture Standard

Each fixture should name:

- the failure mode it represents;
- the source report or external example that motivated it;
- the scenario a reviewer or worker agent would see;
- the controls that should catch the regression;
- the expected output fields or behavior;
- the backlog items that would implement or verify the control.

Fixtures are intentionally small. They are not full benchmark tasks yet; they
are the contract that future prompt/schema tests should compile into executable
checks.

## Validation

Run:

```sh
python3 scripts/validate_agentic_regression_artifacts.py
```

The validator is intentionally stdlib-only. It checks that the seed fixture
suite references real source reports, real backlog IDs, and receipt fields that
exist in `schemas/session-receipt.schema.json`. It also compiles every fixture
into a draft task packet in memory and verifies the permission-policy example
preserves the read-only browser/reviewer safety guarantees.

To materialize executable handoff packets for review, run:

```sh
python3 scripts/validate_agentic_regression_artifacts.py --emit-task-packets /tmp/codex-codereview-fixture-packets
```

The emitted packets are generated artifacts. They are useful for choosing and
running a fixture, but the source of truth remains the seed fixture suite.

## Golden Harness

Run:

```sh
python3 scripts/run_agentic_regression_fixtures.py
```

This deterministic harness checks every seed fixture against the local
prompt/schema/policy artifacts it is supposed to protect. It is not a model
benchmark; it catches local workflow regressions such as dropped false-positive
notes, missing red/green receipt fields, missing read-only policy controls, and
missing context-packet guidance.

For machine-readable output:

```sh
python3 scripts/run_agentic_regression_fixtures.py --json
```
