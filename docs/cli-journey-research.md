# CLI Journey Research

Generated: 2026-06-26T08:45:54Z

This report summarizes local Codex thread history to improve kit CLI
journeys. Raw thread text stays in local Codex storage and local mining
artifacts; this tracked report contains aggregate, redacted findings only.

## Corpus

- Threads scanned: 1228
- Developer threads classified: 1162
- Skipped as non-dev: 66
- Date range: 2025-08-09T03:08:29Z to 2026-06-26T08:45:30.719Z

## Route Signals

| Signal | Count |
| --- | ---: |
| `shell-git-only` | 559 |
| `unknown` | 344 |
| `make-agent` | 191 |
| `mixed` | 67 |
| `direct-script` | 1 |

## Journey Signals

| Signal | Count |
| --- | ---: |
| `recovery` | 535 |
| `release-gated` | 355 |
| `clean-maintenance` | 151 |
| `unknown` | 59 |
| `dirty-work` | 49 |
| `fresh-repo` | 13 |

## Intent Signals

| Signal | Count |
| --- | ---: |
| `fix` | 739 |
| `release` | 355 |
| `update` | 33 |
| `unknown` | 21 |
| `review` | 4 |
| `docs` | 4 |
| `setup` | 4 |
| `research` | 2 |

## Friction Signals

| Signal | Count |
| --- | ---: |
| `retry-loop` | 702 |
| `clarification-needed` | 620 |
| `wrong-repo-risk` | 340 |
| `command-confusion` | 250 |
| `failed-command` | 139 |
| `stale-docs` | 129 |
| `missing-json-field` | 110 |
| `unexpected-mutation-risk` | 103 |
| `direct-script-fallback` | 59 |

## Top Commands

| Signal | Count |
| --- | ---: |
| `sed -n` | 716 |
| `rg -n` | 670 |
| `git status` | 427 |
| `write_stdin` | 412 |
| `apply_patch` | 377 |
| `nl -ba` | 371 |
| `update_plan` | 314 |
| `patch_apply_end` | 300 |
| `python3 -` | 289 |
| `pwd &&` | 230 |

## Recommended Backlog

- Prioritize CLI-first wrappers so agents do not need direct `python3 scripts/repo_contract_kit.py` fallbacks.
- Keep `make agent-*` compatibility, but document the equivalent `kit` JSON route beside each target.
- Add or expand CLI UX fixtures around commands that produced parse errors or unknown-command failures.
- Treat stale-doc findings as docs-contract backlog and add freshness checks where possible.
- Make source-repo vs target-repo language more explicit in `kit start`, setup, update, and maintainer docs.
- Promote frequently consumed JSON fields into stable payload contracts or generated schema files.

## Confidence Notes

- Classification is deterministic and heuristic-based.
- Counts indicate repeated signals, not statistically clean telemetry.
- Thread ids are hashed in local summaries and omitted from this report.
- Command names are normalized; raw prompts, raw outputs, secrets, and full paths are not included here.
