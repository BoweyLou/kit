# Vision

repo-contract-kit exists to make repository operating expectations explicit,
local, and enforceable.

Documentation freshness is still the first contract, but the project now covers
the wider local guardrail surface that agent-assisted repositories need:
documentation impact, agent instructions, review policy, evidence receipts, TDD
expectations, and optional workflow profiles.

## Problem

In agent-heavy development, code can be produced quickly, but documentation,
tests, comments, prompts, and local operating rules often lag because the repo
does not define what must change when code changes.

This creates:

- stale READMEs
- forgotten config docs
- broken quickstarts
- undocumented behavior changes
- architectural amnesia
- stale agent instructions
- review noise without evidence
- claims of test-first work without red/green proof

## Vision

A repository should be able to say:

- what counts as documentation impact
- what documentation must change for each class of code change
- how local contributors get feedback
- how local checks enforce compliance before any hosted service is involved
- how optional CI adapters can mirror the local checks when a host supports them
- when architectural decisions must be recorded
- which local agent workflows are approved
- what evidence must be captured before agent work is trusted
- when TDD or executable specs are expected

## Outcome

The long-term goal is a reusable repo kit plus automation that helps solo
developers and agent-assisted teams adopt local repository guardrails without
enterprise ceremony or a dependency on GitHub Actions.
