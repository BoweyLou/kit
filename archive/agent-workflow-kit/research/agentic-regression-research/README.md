# Agentic Regression Raw Research

Generated: 2026-05-05

This folder contains raw source inventories for agentic coding regression research.
The reports are intentionally unsynthesized and source-heavy.

| Surface | Report | Source count | Method note |
| --- | --- | ---: | --- |
| X | `2026-05-05-x-raw.md` | 123 | Authenticated read-only browser search extraction; no account mutations were performed. |
| GitHub | `2026-05-05-github-raw.md` | 130 | Authenticated read-only GitHub Search API collection; secondary rate-limit warnings are recorded in the report. |
| Hacker News | `2026-05-05-hn-raw.md` | 125 | Read-only Algolia HN search and search-by-date collection. |

No account mutations were performed on X, GitHub, or Hacker News.

## Follow-On Artifacts

- `2026-05-06-findings.md`: synthesis and roadmap from the raw reports.
- `fixtures/`: seed regression fixtures for `AGW-056`, with follow-on controls
  such as the `AGW-098` closeout-first startup guard.
- `../../schemas/agentic-regression-fixture.schema.json`: fixture suite schema.
- `../../schemas/agent-permission-policy.schema.json`: permission policy schema
  for `AGW-057`.
- `../../scripts/validate_agentic_regression_artifacts.py`: stdlib harness for
  validating the seed fixtures, checking required receipt fields, verifying the
  permission-policy example, and emitting draft task packets for fixture runs.
- `../../scripts/run_agentic_regression_fixtures.py`: deterministic golden
  harness that checks each seed fixture against the local prompt, schema, and
  policy artifacts it is meant to protect, including closeout-first startup
  language for unfinished prior task state.
