# Concepts for Beginners

## Pull Request (PR)

A pull request is just a reviewable bundle of changes.
Even if you work alone, PRs are useful because they provide a clean summary screen and a place for automated checks to run.

## CI

CI means continuous integration.
In practice, it just means: when changes are proposed, the platform automatically runs checks.

For this kit, CI is where the repository can say things like:
- docs still build
- required documentation files exist
- generated docs are not stale
- code changes with documentation impact are not missing doc changes

## Hooks

Hooks are local scripts that run automatically before commits or pushes.
They are useful for quick feedback.
They are not enough by themselves because they can be skipped.

## AGENTS.md

AGENTS.md is a repo-local instruction file for coding agents.
It tells the agent what the repo expects, including documentation obligations.

## ADR

ADR means Architecture Decision Record.
It is a small file explaining an important technical decision and why it was made.

## Documentation contract

A documentation contract is a set of explicit rules saying:
when this kind of change happens, these documentation actions are required.

That is the central idea in this kit.
