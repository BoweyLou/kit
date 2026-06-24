---
name: repo-doc-contract-bootstrap
description: Bootstrap the repo-contract-kit starter files into a target repository and explain the installed system in beginner-friendly terms.
version: 0.1.0
author: Yannick Bowe and Hermes Agent
license: MIT
---

# repo-doc-contract-bootstrap

## Purpose

Install the repo-contract-kit starter files into a repository so documentation
expectations, local agent workflows, and evidence requirements become explicit
and enforceable.

## When to use

Use this when:
- a repository has documentation drift
- coding agents are making changes without updating docs
- the user wants a calm first step toward hooks, CI, and PR-based workflows

## Procedure

1. Confirm the target path is a git repo.
2. Inspect whether docs/, .github/, and scripts/ already exist.
3. Choose a preset or profile:
   - `minimal` for the documentation contract only.
   - `learning` for docs plus review/learning prompts.
   - `test-first` for docs plus executable-spec prompts.
   - `agentic` for docs, review prompts, learning prompts, and test-first prompts.
4. Install or update the starter files and `doc-contract.json` from repo-contract-kit.
5. Explain what was installed in beginner-friendly language.
6. Run `make docs-check` if the target repo has the installed files.
7. For agentic presets, point the user at `make agent-review`, `make agent-learn`, and `make agent-test-first`.
8. Summarize any collisions or manual follow-up.

## Important rule

Do not silently overwrite existing files unless the user asked for it or the workflow explicitly supports force mode.
