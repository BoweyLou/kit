# CLI Journey Research

Generated: 2026-06-27T01:58:52Z

This report summarizes local Codex thread history to improve kit CLI
journeys. Raw thread text stays in local Codex storage and local mining
artifacts; this tracked report contains aggregate, redacted findings only.

The baseline section covers all local development-looking threads. The
kit/current-era section narrows the view to kit-related evidence since
2026-06-25T00:00:00Z.

## Baseline All-Dev Corpus

All local development-looking Codex threads, including non-kit work. Use this as agent workflow telemetry rather than pure kit telemetry.

- Threads scanned: 1235
- Developer threads classified: 1169
- Skipped as non-dev: 66
- Skipped by filter: 0
- Date range: 2025-08-09T03:08:29Z to 2026-06-27T01:58:27.322Z

### Route Signals

| Signal | Count |
| --- | ---: |
| `shell-git-only` | 564 |
| `unknown` | 344 |
| `make-agent` | 191 |
| `mixed` | 69 |
| `direct-script` | 1 |

### Journey Signals

| Signal | Count |
| --- | ---: |
| `recovery` | 536 |
| `release-gated` | 360 |
| `clean-maintenance` | 152 |
| `unknown` | 59 |
| `dirty-work` | 49 |
| `fresh-repo` | 13 |

### Intent Signals

| Signal | Count |
| --- | ---: |
| `fix` | 741 |
| `release` | 360 |
| `update` | 33 |
| `unknown` | 21 |
| `review` | 4 |
| `docs` | 4 |
| `setup` | 4 |
| `research` | 2 |

### Friction Signals

| Signal | Count |
| --- | ---: |
| `clarification-needed` | 626 |
| `command-confusion` | 195 |
| `failed-command` | 139 |
| `stale-docs` | 133 |
| `missing-json-field` | 111 |
| `retry-loop` | 105 |
| `wrong-repo-risk` | 74 |
| `direct-script-fallback` | 61 |
| `unexpected-mutation-risk` | 51 |

### Kit Commands

| Signal | Count |
| --- | ---: |
| `kit status` | 6 |
| `kit setup` | 5 |
| `kit update` | 3 |
| `kit doctor` | 2 |
| `kit start` | 2 |
| `kit agent-context` | 1 |

### Make Commands

| Signal | Count |
| --- | ---: |
| `make kit-status` | 114 |
| `make agent-start` | 87 |
| `make version-status` | 87 |
| `make agent-task-status` | 84 |
| `make docs-check` | 69 |
| `make backlog-status` | 68 |
| `make agent-next` | 59 |
| `make backlog-check` | 58 |
| `make agent-verify` | 43 |
| `make version-check` | 40 |

### Shell Commands

| Signal | Count |
| --- | ---: |
| `sed -n` | 730 |
| `rg -n` | 688 |
| `git status` | 441 |
| `nl -ba` | 415 |
| `ls` | 351 |
| `find` | 345 |
| `python3 -` | 315 |
| `pwd` | 291 |
| `get_project_context` | 247 |
| `rg --files` | 227 |

### Agent Tool Calls

| Signal | Count |
| --- | ---: |
| `apply_patch` | 451 |
| `write_stdin` | 431 |
| `patch_apply_end` | 364 |
| `update_plan` | 330 |

## Kit-Related Current-Era Corpus

Kit-related threads since the unified public kit repo work began. Use this narrower slice for current CLI journey decisions.

- Threads scanned: 1235
- Developer threads classified: 37
- Skipped as non-dev: 66
- Skipped by filter: 1132
- Date range: 2026-06-15T03:51:08.164Z to 2026-06-27T01:58:27.322Z
- Since filter: latest thread timestamp at or after 2026-06-25T00:00:00Z
- Kit-related filter: enabled

### Route Signals

| Signal | Count |
| --- | ---: |
| `shell-git-only` | 25 |
| `make-agent` | 6 |
| `mixed` | 6 |

### Journey Signals

| Signal | Count |
| --- | ---: |
| `recovery` | 20 |
| `release-gated` | 17 |

### Intent Signals

| Signal | Count |
| --- | ---: |
| `fix` | 20 |
| `release` | 17 |

### Friction Signals

| Signal | Count |
| --- | ---: |
| `clarification-needed` | 25 |
| `command-confusion` | 12 |
| `stale-docs` | 6 |
| `direct-script-fallback` | 5 |
| `missing-json-field` | 5 |
| `wrong-repo-risk` | 4 |
| `unexpected-mutation-risk` | 3 |

### Kit Commands

| Signal | Count |
| --- | ---: |
| `kit start` | 2 |

### Make Commands

| Signal | Count |
| --- | ---: |
| `make kit-status` | 8 |
| `make agent-start` | 7 |
| `make version-status` | 7 |
| `make backlog-status` | 6 |
| `make goal-check` | 5 |
| `make agent-next` | 4 |
| `make backlog-check` | 4 |
| `make version-check` | 3 |
| `make agent-task-status` | 3 |
| `make docs-lint` | 3 |

### Shell Commands

| Signal | Count |
| --- | ---: |
| `rg -n` | 37 |
| `sed -n` | 35 |
| `nl -ba` | 30 |
| `git status` | 27 |
| `get_project_context` | 20 |
| `rg --files` | 16 |
| `pwd` | 16 |
| `git diff` | 16 |
| `ls` | 14 |
| `find` | 14 |

### Agent Tool Calls

| Signal | Count |
| --- | ---: |
| `apply_patch` | 17 |
| `patch_apply_end` | 17 |
| `write_stdin` | 12 |
| `update_plan` | 3 |

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
