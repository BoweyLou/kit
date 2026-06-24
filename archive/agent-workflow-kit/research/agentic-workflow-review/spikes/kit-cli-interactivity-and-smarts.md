# Kit CLI Interactivity And Smarts Research Packet

Date: 2026-06-23

Status: complete research packet, no shipped runtime behavior.

## Question

How should `kit` become more intuitive and useful for both humans and agents,
without losing its current local-first, docs-as-code, non-mutating-by-default
guardrails?

This packet samples:

- the live `kit` operator surface in this checkout
- Hacker News discussions about good and bad CLI experience
- X/social discussion around agent-native CLIs
- GitHub and vendor examples of strong CLI patterns

## Recommendation

Do not start with a big TUI rewrite. The highest-leverage improvement is a
smarter command contract around the existing Python CLI:

1. Add `kit agent-context --json` or `kit command-map --json` as a stable,
   versioned description of the CLI command tree, flags, mutating behavior,
   output modes, examples, aliases, and schemas.
2. Rework top-level help into three lanes: daily human commands, agent/automation
   commands, and maintainer commands. Keep `kit --help` short; move the full
   command inventory behind `kit help --all`.
3. Add agent-safe parse errors: did-you-mean suggestions, valid value lists,
   concrete next commands, and a JSON error envelope when JSON/agent mode is
   requested.
4. Add shell completions and a TTY-only command palette. The command palette
   should preview the exact command it will run and must disable itself under
   `--no-input`, non-TTY stdin/stdout, or agent mode.
5. Add a compact update/doctor summary layer so large JSON plans and conflict
   lists are readable by humans while still preserving full machine output.

The design principle is "progressive disclosure over cleverness": humans should
see the next safe action quickly, and agents should get a compact, parseable
description of the same action surface.

## Current Kit Surface

Observed from `/Volumes/Myrtle/Code/04_Code/Codex_CodeReview` on 2026-06-23.

Commands sampled:

- `kit`
- `kit --help`
- `kit options`
- `kit help --all`
- `kit status`
- `kit status --json`
- `kit doctor`
- `kit doctor --json`
- `kit self status`
- `kit self status --json`
- `kit update --dry-run --json`
- `kit agent-context-bundle --json`
- invalid command/error probes through the installed entrypoint

Live state:

- Current checkout is clean on `main`.
- Target repo reports `repo-contract-kit` installed at `0.6.5`.
- The global `kit` launcher source reports tool version `0.5.0` at detached
  ref `edd21c27cfc0`.
- `kit status --json` exposes useful metadata including `schema_version`,
  `cli.mutating_commands`, `cli.sidecar_write_commands`,
  `target_repo_writes`, `sidecar_writes`, and sidecar paths.
- `kit doctor --json` reports blockers, warnings, worktree state, task state,
  receipts, and recommendations with clear non-mutating metadata.
- `kit update --dry-run --json` produces a detailed update plan with conflicts,
  actions, after-update commands, and explicit `target_repo_writes.performed:
  false`.

Strengths:

- `kit` with no arguments already acts as a light guided dashboard.
- `kit options` is much clearer than raw argparse help.
- JSON output exists for many important agent commands.
- Mutating commands and sidecar-write commands are explicitly listed in CLI
  metadata.
- Dry-run/update-plan behavior is conservative and preserves customized target
  files by writing proposals instead of overwriting them.
- Doctor/preflight/state-ledger style commands already match agent-safe
  workflow needs.

Current friction:

- `kit --help` presents the full subcommand list in one flat argparse block.
  This is hard for new humans and wasteful for agents.
- `kit help --all` is curated, but it is not a structured command inventory.
- `kit agent-context-bundle --json` describes repo/task context, not the `kit`
  command surface. Agents still have to infer commands from prose help or source.
- Invalid commands use default argparse errors. They enumerate all choices, but
  they do not suggest likely commands, do not show the next useful command, and
  do not emit a structured JSON error envelope.
- There is no visible shell completion surface.
- There is no global `--no-input` or `--agent` contract. The current dashboard
  correctly avoids interaction in non-TTY mode, but the policy is implicit.
- Human output does not call out the global-tool-vs-target-install version
  mismatch clearly. `kit self status` says tool `0.5.0`; `kit status` says target
  `0.6.5`. Both are true, but the mental model is not obvious.
- `kit update --dry-run --json` is excellent for machines but too long for a
  human first read. A compact summary should lead, with details available after.
- Several command names are aliases or near-aliases (`doctor`,
  `agent-doctor`, `agent-preflight`, `target doctor`; `setup`, `install`,
  `target add`). That may be necessary, but the aliases need to be surfaced as
  compatibility or audience-specific routes.

## Source Evidence

### Hacker News

- "Command line interface guidelines" discussion:
  <https://news.ycombinator.com/item?id=39273932>. The thread debates the
  human-readable versus machine-readable tension and points toward explicit
  machine output modes such as `--json`.
- "CLI Guidelines" discussion:
  <https://news.ycombinator.com/item?id=25304257>. A useful lead for
  machine-readable method/option documentation, not only human help text.
- "Good examples of interactive command-line user experience":
  <https://news.ycombinator.com/item?id=14401057>. Useful leads include Heroku
  CLI style guidance, exit status importance, fzf speed/intuitiveness, prompt
  toolkit, and the reminder that an interactive interface should map to exact
  plain CLI commands.
- "Best and worst command-line interfaces":
  <https://news.ycombinator.com/item?id=29329607>. The Docker example is a good
  discoverability model: no-arg help, logically grouped command tree, examples,
  and subcommand-specific help. The tar contrast shows how dense flag surfaces
  become unusable despite being powerful.
- "CLI user experience case study":
  <https://news.ycombinator.com/item?id=38966601>. The thread calls out stdout,
  stderr, pipes, and autocomplete as core CLI design rather than incidental
  implementation details.
- "12 Factor CLI Apps":
  <https://news.ycombinator.com/item?id=18172689>. Useful as a warning that big
  help screens become a forest, while completions often fail because per-app
  completion machinery is missing.
- "Building a CLI for all of Cloudflare":
  <https://news.ycombinator.com/item?id=47753689>. Strong current signal for
  agent-facing CLIs: permissions checks, first-try success, discoverability,
  no interactive behavior from help flags, completions matching real commands,
  and consistent output across subcommands.
- "Principles for agent-native CLIs":
  <https://news.ycombinator.com/item?id=48052333>. The discussion pushes back
  against agent-only design and argues for human plus programmatic automation
  first. That is the right constraint for `kit`.

### X / Social

Direct X pages were login-limited in this browser session, so X material below
is treated as lead evidence unless backed by readable sources.

- Trevin Chow's X thread was the linked source for the HN "Principles for
  agent-native CLIs" discussion. The readable long-form version is:
  <https://trevinsays.com/p/10-principles-for-agent-native-clis>.
- Public search snippets around the same discussion emphasize uniform
  structured output, no interaction for agent calls, parseable responses, and
  bounded output. Relevant X leads:
  <https://x.com/trevin/status/2051316002730991795>,
  <https://x.com/ndimares/status/2039028199615574321>,
  <https://x.com/rlaope/status/2065721175716815150>,
  <https://x.com/daniel_mac8/status/2009036047254970448>.
- Treat the X signal as zeitgeist, not authority: it is useful because it names
  agent pain points, but implementation decisions should rest on local evidence,
  primary docs, and tested behavior.

### GitHub And Primary Examples

- Command Line Interface Guidelines: <https://clig.dev/>. Relevant rules:
  machine-readable output where useful, `--no-input` disables prompts, state
  changes should be explained, errors should teach, stdin/stdout/stderr matter,
  and CLI interfaces need compatibility discipline.
- Heroku CLI Style Guide:
  <https://devcenter.heroku.com/articles/cli-style-guide>. Useful for restrained
  color and TTY-aware output; color must be disableable and warnings/errors
  should carry semantic weight.
- GitHub CLI manual: <https://cli.github.com/manual/gh_help_reference>. `gh`
  repeatedly exposes JSON output, jq filtering, templates, completions, and
  browser-opening as explicit modes rather than hidden behavior.
- GitHub CLI repo: <https://github.com/cli/cli>. The product framing is clear:
  bring GitHub concepts into the terminal where users already work with `git`
  and code.
- Charm Gum: <https://github.com/charmbracelet/gum>. Good pattern library for
  small composable interactive prompts. It argues for ready-to-use components,
  not a bespoke TUI for every tool.
- Charm Bubble Tea: <https://github.com/charmbracelet/bubbletea>. Good if a real
  TUI becomes necessary, but heavier than `kit` needs for the next step.
- Textualize Trogon: <https://github.com/Textualize/trogon>. Interesting
  pattern: generate a TUI from the CLI definition. It is most relevant if `kit`
  ever migrates from argparse to Click/Typer; it is not a near-term reason to
  rewrite.
- Typer: <https://github.com/fastapi/typer>. Relevant for Python CLIs with typed
  command definitions and completion support, but a migration should be justified
  by command-contract gains rather than aesthetics.
- Rich: <https://github.com/textualize/rich>. Useful for human tables and
  summaries, but it must remain optional or carefully gated because startup time
  and plain output matter.
- Python Prompt Toolkit:
  <https://github.com/prompt-toolkit/python-prompt-toolkit>. Useful for a
  TTY-only command palette with search/completion.
- agentnative CLI linter docs: <https://docs.rs/agentnative>. Useful checklist:
  non-interactive by default, structured output, progressive help, actionable
  errors, safe retries, composable structure, bounded responses, and discoverable
  skill bundles.
- Tilebox CLI release: <https://tilebox.com/blog/cli-release-v0.1.0>. Current
  example of human and agent design: consistent vocabulary, every command has
  `--json`, structured discovery through `agent-context`, file-based input,
  async-aware workflows, bounded pagination, and actionable validation.
- Cloudflare "Building a CLI for all of Cloudflare":
  <https://blog.cloudflare.com/cf-cli-local-explorer/>. Strong example of using
  schemas, linting, and guardrails to generate CLI/API/docs/agent surfaces from
  one source.
- Cloudflare Code Mode:
  <https://blog.cloudflare.com/code-mode-mcp/>. Important adjacent lesson: keep
  agent context compact through progressive discovery rather than loading a huge
  static tool surface.

## Design Principles For Kit

### 1. One Command Surface, Three Audiences

`kit` should stay the one public command, but its help should route by audience:

- Humans: setup, status, update preview/apply, doctor, options.
- Agents: command-map, context bundle, state ledger, doc-impact, goal-check,
  task-packet, verify, machine-readable dry runs.
- Maintainers: self update/status, target management, migrate-config, install,
  source checkout repair.

The current command set already has these audiences. The missing piece is an
explicit map that says which command belongs where and which aliases are
compatibility routes.

### 2. Structured Discovery Before TUI

Add a machine-readable command map before adding a rich interactive interface.
Suggested shape:

```json
{
  "schema_version": 1,
  "command": "agent-context",
  "cli": {
    "name": "kit",
    "tool_version": "0.5.0",
    "target_install_version": "0.6.5"
  },
  "commands": [
    {
      "path": ["update"],
      "audience": ["human", "agent"],
      "summary": "Update the current target repo, or use --global for the tool checkout.",
      "mutates_target_by_default": true,
      "safe_preview": "kit update --dry-run",
      "json_supported": true,
      "non_interactive_supported": true,
      "aliases": [["target", "update"]],
      "examples": [
        "kit update --dry-run",
        "kit update --dry-run --json",
        "kit update"
      ]
    }
  ],
  "exit_codes": {
    "0": "success",
    "2": "usage error"
  }
}
```

This can be generated from the existing argparse parser plus a small metadata
registry for audience, mutation class, examples, and output schemas.

### 3. Human Help Should Lead With Scenarios

`kit options` is already better than `kit --help`. Make it the model for all
human help:

- "I am setting up a repo"
- "I want to update safely"
- "Something is dirty or blocked"
- "I am an agent and need JSON"
- "I am maintaining the global tool"

Each scenario should print two or three commands, not a full command inventory.

### 4. Errors Are The Highest-Signal Teaching Surface

Default argparse errors are technically correct but not enough. Invalid command
`statuz` should become:

```text
error: unknown command "statuz"
did you mean: kit status

Common commands:
  kit status
  kit doctor
  kit options

Run `kit help --all` for the full command list.
```

With JSON/agent mode:

```json
{
  "schema_version": 1,
  "command": null,
  "error": {
    "type": "unknown-command",
    "message": "unknown command: statuz",
    "suggestions": ["kit status"],
    "next_commands": ["kit options", "kit help --all"]
  },
  "exit_code": 2
}
```

This is also where invalid enum values should list valid values. The agent can
self-correct from the error without reading the whole manual.

### 5. Interactive Means Optional, Exact, And Previewed

Interactive mode should only run when all are true:

- stdin and stdout are TTYs
- `--no-input` is not set
- `KIT_AGENT` or `--agent` is not set
- the selected action is not hidden/destructive without a confirmation contract

The near-term interactive surface should be a command palette:

- fuzzy search commands and scenarios
- show mutation class and dry-run equivalent
- preview exact command line
- enter runs, copy/print command, or quit
- no alternate-screen dependency at first

This keeps the shell-native path first and avoids making `kit` depend on a TUI
library before its command contract is stable.

### 6. Make The Version Model Obvious

The current state can show:

- global tool source version: `0.5.0`
- target installed kit version: `0.6.5`

That is confusing because the words "kit version" can refer to either. Human
status should render it as:

```text
tool checkout: 0.5.0 at edd21c2 (detached)
target install: 0.6.5 from d4d7910
note: target files are newer than the global launcher source
next: run `kit update --global`, then `kit status`
```

If the mismatch is acceptable, say why. If it is stale, say the safe next
command.

### 7. Compact First, Full Detail On Demand

Long JSON plans should keep their full detail, but human output should lead with
a summary:

```text
Update preview for Codex_CodeReview
 - safe direct updates: 3
 - conflicts preserved as proposals: 5
 - target-owned files unchanged: 66
 - blockers: 0
 - would write on apply: yes

Next:
  1. Review proposals: .doc-contract-kit/updates/20260623T001606Z/
  2. Apply safe updates: kit update
  3. Re-run checks: kit doctor && make docs-check

Run `kit update --dry-run --json` for full machine output.
```

### 8. Keep Smartness Local And Explainable

Avoid "AI inside the CLI" for now. The right smarts are deterministic:

- command map and examples
- did-you-mean suggestions
- next safe command recommendations
- conflict summaries
- version mismatch explanations
- docs/task/context summaries
- feedback ledger for recurring friction

This keeps `kit` usable by both humans and agents without network calls, model
dependencies, or hidden policy decisions.

## Proposed Implementation Slices

### P0: Command Map And Agent Context

Add `kit command-map --json` and alias `kit agent-context --json`.

Acceptance criteria:

- emits schema-versioned JSON
- includes commands, flags, summaries, examples, audience, mutation class,
  sidecar write behavior, JSON support, aliases, and output schema pointers
- generated from or checked against the argparse parser so it cannot drift
- includes golden tests for at least setup, status, update, doctor, target
  update, task-packet, agent-context-bundle, and invalid command metadata
- docs explain that this is the preferred machine introspection surface

### P0: Better Errors

Replace bare argparse parse failures with a small custom parser/error adapter.

Acceptance criteria:

- unknown command suggests nearest valid command
- invalid enum/value errors list valid values where available
- error text includes one or two concrete next commands
- `--json` or `KIT_AGENT=1` emits a stable JSON error envelope
- stdout/stderr behavior is documented and tested

### P0: Help Grouping And Version Explanation

Make `kit --help` and `kit status` less ambiguous.

Acceptance criteria:

- top-level help shows core lanes and points to `kit help --all`
- full command inventory remains available
- human status distinguishes global tool checkout, target install, prompt
  snapshot, and source refs
- stale or mismatched tool/target versions produce explicit next commands

### P1: Shell Completion

Add `kit completion bash|zsh|fish`.

Acceptance criteria:

- completion output is generated from the same command map/parser metadata
- completions include subcommands and common flags
- docs show install snippets
- no completion command mutates shell config by default

### P1: TTY Command Palette

Add `kit palette` or enhance no-arg `kit` when TTY is detected.

Acceptance criteria:

- no interactive behavior in non-TTY, `--no-input`, or agent mode
- fuzzy search over scenarios and commands
- preview exact command and mutation class
- support "print command" as well as "run command"
- use prompt_toolkit or a minimal dependency-light implementation first

### P1: Compact Update And Doctor Summaries

Keep full JSON but improve human summaries.

Acceptance criteria:

- `kit update --dry-run` begins with counts, blockers, conflicts, direct updates,
  target-owned files, proposal path, and next commands
- `kit doctor` groups blockers, warnings, and recommendations by actionability
- detailed lists are available with `--verbose` or JSON

### P2: Local Feedback Ledger

Add `kit feedback "..."` for humans and agents to record CLI friction locally.

Acceptance criteria:

- writes JSONL under sidecar/global state, not target repo
- includes command, cwd/repo id, timestamp, tool version, target version, and
  optional last error context
- no upstream network by default
- `kit feedback list --json` exposes entries for maintainers

## What Not To Do

- Do not make a full-screen TUI the only way to use `kit`.
- Do not add hidden network calls or model calls.
- Do not hide mutating behavior behind friendly wording.
- Do not make `kit update` smarter by silently resolving conflicts.
- Do not break existing JSON fields without a versioned deprecation path.
- Do not solve help density by moving everything into `AGENTS.md`.
- Do not migrate from argparse to Typer/Click unless the command contract,
  completions, and tests justify the churn.

## Backlog Candidates

These are candidate follow-on slices for `repo-contract-kit`, not changes made
by this research packet.

| ID | Priority | Candidate | Notes |
| --- | --- | --- | --- |
| `AGW-107` | P0 | Add `kit command-map` / `kit agent-context` | Foundation for agents, completions, generated docs, and TTY palette. |
| `AGW-108` | P0 | Add structured parse errors and did-you-mean suggestions | Improves both human recovery and agent retry behavior. |
| `AGW-109` | P0 | Rework top-level help/status grouping | Reduces first-run confusion, especially tool-vs-target version mismatch. |
| `AGW-110` | P0 | Define non-interactive and agent-mode contract | Makes TTY prompts, JSON errors, and script behavior explicit. |
| `AGW-111` | P1 | Compact update/doctor human summaries | Keeps detailed JSON while improving operator scanning. |
| `AGW-112` | P1 | Normalize command aliases and audience lanes | Makes setup/install/target and doctor/preflight routes intentional. |
| `AGW-113` | P1 | Expand JSON consistency and schema pointers | Gives agents stable contracts across command outputs. |
| `AGW-114` | P1 | Add shell completions from parser metadata | Directly addresses HN feedback about discoverability. |
| `AGW-115` | P1 | Add TTY command palette with exact command preview | Human interactivity without weakening scriptability. |
| `AGW-116` | P1 | Generate CLI reference docs and docs-as-tests claims | Keeps command docs aligned with command metadata. |
| `AGW-117` | P1 | Add CLI UX regression fixtures | Protects help, errors, no-input, and summary behavior over time. |
| `AGW-118` | P2 | Add optional polished human renderers | Improves scanning while preserving plain output and `NO_COLOR`. |
| `AGW-119` | P2 | Add local feedback ledger | Captures recurring agent/human friction without external writes. |
| `AGW-120` | P2 | Export command-map-derived agent tool manifest | Lets local agents consume the command contract without scraping help. |
| `AGW-121` | P2 | Add tool-vs-target drift diagnostics | Explains and repairs global launcher versus target install mismatch. |

## Decision Point

If only one item is selected next, choose `AGW-107`.

Reason: the structured command map unlocks the rest. It gives agents a stable
introspection surface, gives humans a source for generated help/completions,
gives tests a contract to prevent drift, and avoids prematurely committing to a
TUI framework.
