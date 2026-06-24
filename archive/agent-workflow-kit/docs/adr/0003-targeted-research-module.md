# ADR 0003: Add A Targeted Research Module

## Status

Accepted

## Context

The workflow kit already supports local-first review, task packets, TDD,
verification, permission policies, and browser research safety. The missing
piece is a structured way to send separate read-only agents after different
source families before changing backlog, review scope, architecture, or design.

Without a module, research runs tend to collapse into one broad web search.
That makes it harder to separate implementation inspiration from academic
methods, official facts, and practitioner pain signals.

## Decision

Add a targeted research workflow under `workflows/prompts/research/`.

The module uses four layers:

1. A research brief defines the question, allowed sources, target output, trust
   profile, and stop conditions.
2. Source-specific prompts collect evidence from GitHub, arXiv, Hacker News, or
   official docs.
3. Source reports record URLs, source quality, evidence grades, caveats, and
   follow-up work.
4. Research synthesis converts accepted evidence into proposed backlog, review,
   architecture, design, ADR, risk, or task-packet outputs.

Research agents stay read-only. They produce proposals only; backlog rows,
ADRs, docs, issues, and code require a separate approved write step.

## Consequences

- `agent-workflow-kit` owns the prompts and schemas for research briefs, source
  reports, and syntheses.
- `repo-contract-kit` can install these prompts and expose local Make targets
  for manual-mode research runs in target repositories.
- Forum, social, and discussion sources remain lead sources unless backed by
  primary evidence.
- GitHub examples must be checked for maintenance, fit, and licensing before
  becoming dependencies or copied implementation.
- Academic papers inform architecture options and evaluation methods; they do
  not automatically become implementation tasks.
