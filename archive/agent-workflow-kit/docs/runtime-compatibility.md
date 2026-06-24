# Runtime Compatibility

Use this matrix when deciding whether a coding-agent runtime should consume a
generated adapter, a planned adapter, or the neutral prompt-kit files manually.

Access date for all external runtime documentation checked here:
2026-06-16.

## Ownership

This legacy checkout owns this compatibility guide as archive and migration
context. Current prompt source, manifest data, source-side generated adapter
definitions, and source-side packaging docs live under
`repo-contract-kit/workflows/`.

`repo-contract-kit` owns target-repo install and update writes. It may install
thin managed runtime adapters in target repositories, but those target files are
install-layer projections, not new source truth for prompt wording.

Installed target repositories own day-to-day runtime state: selected adapters in
`.doc-contract-kit/install.json`, local `AGENTS.md` instructions, ignored
private context, runtime caches, local memories, and any tool-specific files the
team chooses to maintain.

## Status Legend

- **Generated today**: the current `repo-contract-kit/workflows/` source can
  generate or already tracks this source-side artifact; legacy copies may also
  exist in this checkout for comparison.
- **Planned**: recorded in `repo-contract-kit/workflows/manifest.json`, but no
  generated source adapter exists yet.
- **Manual-only**: use the neutral prompt docs or a human-authored thin file;
  this stack does not generate that runtime format.
- **Unsupported/unknown**: do not claim support. Record the uncertainty and use
  manual prompt transfer only if the operator validates the runtime behavior.

## Review-Only Local Model Guidance

Local or self-hosted models are best treated as privacy-oriented first-pass
review tools, not as automatic replacements for stronger or human review. They
fit low-risk review-only work such as documentation scans, duplicate finding
triage, local diff or receipt summarization, and deciding whether private
context should be escalated. They should escalate before conclusions are relied
on for security, privacy, compliance, legal, medical, financial, credential,
account-state, migration, deletion, persistence, public API, build/release,
deployment, production operations, or large-repo architecture risk.

Record the data boundary in receipts or handoff notes:

- `local-only`: inference and review artifacts stay on the machine.
- `self-hosted`: the endpoint is operator-controlled but may be on another
  machine, VM, or private server.
- `remote-openai-compatible`: the API shape is familiar, but prompts and repo
  context still leave the local machine.
- `hosted-provider`: prompts, snippets, diffs, logs, or repository indexes go to
  a hosted provider.
- `unknown`: the boundary was not confirmed; treat output as advisory.

Also record model/provider expectations, context limits, tool-calling and
structured-output caveats, stale-knowledge risk, false-positive or
false-negative concerns, and the escalation decision. Do not claim that local
models are universally private, safe, correct, or productive.

## Compatibility Matrix

| Runtime | Native artifact or instruction surface | Current source artifact | Status | `repo-contract-kit` target install today | Source of truth | Validation source URL and access date | Limitations and privacy/locality notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Codex | `AGENTS.md` files are read before work; Codex skills are directories with `SKILL.md` plus optional scripts, references, assets, and agents. | `.codex/prompts/` is generated from `workflows/prompts/`; `make skill-pack-export` can generate `dist/codex-skill-pack/`. In this checkout those are legacy comparison artifacts. | Generated today. | Vendored `.codex/prompts/` snapshots are installed by the review-prompt/test-first profiles. This source checkout has no explicit runtime adapters selected in `.doc-contract-kit/install.json`. | For current edits, use `repo-contract-kit/workflows/prompts/` and `repo-contract-kit/workflows/manifest.json`; use this checkout only for archive comparison. | [OpenAI Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md), accessed 2026-06-16; [OpenAI Codex skills](https://developers.openai.com/codex/skills), accessed 2026-06-16; [OpenAI Codex CLI](https://developers.openai.com/codex/cli), accessed 2026-06-16; [OpenAI Codex advanced configuration](https://developers.openai.com/codex/config-advanced), accessed 2026-06-16; [OpenAI Codex local environments](https://developers.openai.com/codex/app/local-environments), accessed 2026-06-16. | Keep private, user, and repo-specific state out of generated shared prompts. OpenAI Codex local environments configure worktree setup/actions, not generated prompt support. Codex CLI documents OSS mode for local providers such as Ollama or LM Studio, so receipts should record whether the run was `local-only`, `self-hosted`, `remote-openai-compatible`, `hosted-provider`, or `unknown`, plus capability caveats. |
| Claude Code | Project instructions and memory are centered on Claude Code memory surfaces such as `CLAUDE.md` and per-project memory under `~/.claude/projects/<project>/memory/`. | `repo-contract-kit/workflows/manifest.json` lists planned `CLAUDE.md` and `.claude/commands/` outputs; no source-generated Claude adapter exists yet. | Planned for source generation. | The companion install layer supports an optional thin `claude-code` adapter that writes managed `CLAUDE.md`; that is install-layer routing, not source-generated prompt support. | Source generation starts in `repo-contract-kit/workflows/manifest.json` and `repo-contract-kit/workflows/prompts/`; target installs are selected through `repo-contract-kit`. | [Claude Code memory docs](https://code.claude.com/docs/en/memory), accessed 2026-06-16. | Treat Claude auto memory and per-user memory files as local runtime state, not shared prompt-kit source. Do not copy private project memory into generated adapters. |
| Cursor | Cursor rules use Project, Team, and User Rules plus `AGENTS.md`; project rules are stored in `.cursor/rules` and, per the current docs page source, use `.mdc` files. | `repo-contract-kit/workflows/manifest.json` lists planned `.cursor/rules/*.mdc` outputs; no generated Cursor adapter exists yet. | Planned; current use is manual-only. | No Cursor adapter is installed by `repo-contract-kit` today. | Source generation starts in `repo-contract-kit/workflows/manifest.json` and `repo-contract-kit/workflows/prompts/`; until then, use `AGENTS.md` or manually maintained Cursor rules. | [Cursor Rules](https://cursor.com/docs/rules), accessed 2026-06-16. | The Cursor docs page is JavaScript-rendered, so keep claims conservative: project rules, user/team rules, and `AGENTS.md` are documented, but this repo does not generate Cursor rule metadata yet. |
| Continue | Local rules are files in `.continue/rules`; Continue applies rules in Agent, Chat, and Edit modes. | `repo-contract-kit/workflows/manifest.json` lists planned `.continue/rules/*.md` outputs; no generated Continue adapter exists yet. | Planned; current use is manual-only. | No Continue adapter is installed by `repo-contract-kit` today. | Source generation starts in `repo-contract-kit/workflows/manifest.json` and `repo-contract-kit/workflows/prompts/`; until then, use neutral prompt docs manually. | [Continue rules](https://docs.continue.dev/customize/rules), accessed 2026-06-16; [Continue Ollama provider](https://docs.continue.dev/customize/model-providers/top-level/ollama), accessed 2026-06-16. | Continue also supports Hub rules. Do not publish repo-private guidance to Hub without review; keep generated support pending until validation and install ownership are defined. Continue's Ollama provider can point at a remote endpoint, and model capabilities or context length may need explicit configuration, so local-model receipts should record the endpoint boundary and capability caveats. |
| GitHub Copilot | Repository-wide instructions use `.github/copilot-instructions.md`; path-specific files use `.github/instructions/**/*.instructions.md`; supported environments also vary in `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` support. | `.github/copilot-instructions.md` is generated from the shared source. Path-specific `.instructions.md` files are not generated by this repo today. | Generated today for repository-wide instructions only. | The companion install layer supports an optional thin `github-copilot` adapter that writes managed `.github/copilot-instructions.md`. | Edit the shared prompt source in `repo-contract-kit/workflows/`, regenerate the Copilot adapter, and install/update selected target files through `repo-contract-kit`. | [GitHub repository instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions), accessed 2026-06-16; [GitHub custom instructions support](https://docs.github.com/en/copilot/reference/custom-instructions-support), accessed 2026-06-16; [VS Code custom instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions), accessed 2026-06-16. | GitHub.com and IDE support differ. Hosted Copilot agents may receive repository context, so do not place secrets, private local paths, or unreviewed user memory in generated instructions. |
| Goose | Project context can use `.goosehints`; persistent instructions can use `GOOSE_MOIM_MESSAGE_TEXT` or `GOOSE_MOIM_MESSAGE_FILE`; `.gooseignore` constrains Developer-extension file access. | None. Use the neutral prompt docs manually if Goose is the active runtime. | Manual-only; generated adapter support is unsupported/unknown. | No Goose adapter is installed by `repo-contract-kit` today. | Manual prompt transfer from `repo-contract-kit/workflows/prompts/` or local docs only; this checkout's prompt tree is legacy comparison material. | [Goose hints](https://goose-docs.ai/docs/guides/context-engineering/using-goosehints/), accessed 2026-06-16; [Goose persistent instructions](https://goose-docs.ai/docs/guides/context-engineering/using-persistent-instructions/), accessed 2026-06-16; [Goose ignore](https://goose-docs.ai/docs/guides/context-engineering/using-gooseignore/), accessed 2026-06-16; [Goose provider configuration](https://goose-docs.ai/docs/getting-started/providers/), accessed 2026-06-16. | `.goosehints` load differently from persistent instructions. `.gooseignore` is scoped to Developer-extension tools and is not a full sandbox. Goose documents local providers such as Ollama, LM Studio, Atomic Chat, Docker Model Runner, and Ramalama, and also hosted or remote-compatible providers such as Ollama Cloud and OpenAI-compatible endpoints; record the exact boundary before treating review output as private. |
| Aider | Coding conventions are manually read from a Markdown file such as `CONVENTIONS.md` via `/read` or `aider --read`; `.aider.conf.yml` can always load convention files. | None. Use the neutral prompt docs manually if Aider is the active runtime. | Manual-only; generated adapter support is unsupported/unknown. | No Aider adapter is installed by `repo-contract-kit` today. | Manual prompt transfer from prompt-kit docs or a repo-owned conventions file. | [Aider coding conventions](https://aider.chat/docs/usage/conventions.html), accessed 2026-06-16; [Aider Ollama](https://aider.chat/docs/llms/ollama.html), accessed 2026-06-16. | Aider convention files are read-only only when loaded that way. Aider documents local Ollama use and warns about small or silently discarded context windows, so review-only local-model use should stay low risk unless context size, model warnings, and output reliability are understood. Keep prompt-kit receipts, task closeout, and privacy rules visible in the active chat instead of assuming Aider loaded them automatically. |
| Cline | Rules live in `.clinerules/`; Cline also recognizes `AGENTS.md`, `~/.agents/AGENTS.md`, `.cursorrules`, and `.windsurfrules`; `.clineignore` controls automatic context loading. | None. Use `AGENTS.md` and neutral prompt docs manually if Cline is the active runtime. | Manual-only; generated adapter support is unsupported/unknown. | No Cline adapter is installed by `repo-contract-kit` today. | Manual prompt transfer from prompt-kit docs or repo-owned Cline rules. | [Cline rules](https://docs.cline.bot/customization/cline-rules), accessed 2026-06-16; [Cline ignore](https://docs.cline.bot/customization/clineignore), accessed 2026-06-16. | `.clineignore` controls automatic loading, not every explicit reference. Do not duplicate long prompt-kit procedures into Cline rules unless there is an owner and freshness check. |
| Roo Code | Preferred rules live under `.roo/rules/` and mode-specific `.roo/rules-{modeSlug}/`; fallback files include `.roorules` and `.roorules-{modeSlug}`; Roo can include `AGENTS.md`; `.rooignore` controls workspace file access. | None. Use `AGENTS.md` and neutral prompt docs manually if Roo Code is the active runtime. | Manual-only; generated adapter support is unsupported/unknown. | No Roo Code adapter is installed by `repo-contract-kit` today. | Manual prompt transfer from prompt-kit docs or repo-owned Roo rules. | [Roo Code custom instructions](https://roocodeinc.github.io/Roo-Code/features/custom-instructions/), accessed 2026-06-16; [Roo Code ignore](https://roocodeinc.github.io/Roo-Code/features/rooignore/), accessed 2026-06-16. | `.rooignore` is workspace-scoped and not a system sandbox. Directory-based rules and fallback files have precedence rules, so avoid generated output until this repo has a validation command for Roo-specific rules. |

## Current Support Summary

- Codex prompt adapters are generated under `.codex/prompts/`; in this checkout
  they are legacy comparison artifacts.
- GitHub Copilot repository instructions are generated under
  `.github/copilot-instructions.md`.
- Codex skill-pack exports are generated on demand under
  `dist/codex-skill-pack/`.
- Claude Code, Cursor, Continue, Windsurf, and plain Markdown outputs remain
  planned in `repo-contract-kit/workflows/manifest.json`.
- Goose, Aider, Cline, and Roo Code are manual or compatibility-note surfaces
  unless a future backlog item adds a real adapter plus validation.
- `repo-contract-kit` currently supports optional thin target adapters for
  `claude-code` and `github-copilot`. That does not mean this legacy checkout
  generates full source adapters for those runtimes.

## Community Runtime Notes

Community projects that use Codex-like names or fork the OpenAI Codex CLI are
not OpenAI Codex support and are not generated adapter targets for this repo.
For example, Open Codex forks advertise multi-provider or Ollama support in
their own repositories, but those claims belong to those community runtimes and
should be treated as manual-only evidence unless this repo adds a validated
adapter. Sources checked: [ymichael/open-codex](https://github.com/ymichael/open-codex),
accessed 2026-06-16; [codingmoh/open-codex](https://github.com/codingmoh/open-codex),
accessed 2026-06-16.

## When Not To Generate An Adapter

Do not add or request a generated adapter when:

- the runtime already reads `AGENTS.md` or another shared instruction surface
  well enough for the task;
- the runtime format is unstable, undocumented, or only known from secondary
  sources;
- the adapter would copy prompt text without preserving required receipts,
  task-packet closeout, validation, privacy, and ownership evidence;
- private user context, local memory, secrets, or ignored files would be copied
  into a hosted runtime without review;
- no owner or validation command exists to keep the adapter current;
- `repo-contract-kit` would need target-repo install/update behavior before the
  source repo can validate the generated output.

## Privacy And Locality Guidance

Keep private context local by default. Generated adapters should contain stable
repo workflow rules, not local memories, secrets, credentials, hidden notes,
tool account state, or one-off user preferences.

Hosted agents and IDE extensions can differ in what they upload, index, or send
to a model provider. Before using hosted Copilot agents, remote providers, Hub
rules, or manually pasted prompt bundles, review whether the target runtime will
receive private repository context or local-only instructions.

Ignored-file controls are runtime-specific and are not interchangeable with
Git, filesystem permissions, or a sandbox. Treat `.gitignore`, `.gooseignore`,
`.clineignore`, `.rooignore`, and Copilot content exclusion as separate layers
with different guarantees. Generated prompt adapters should not rely on one
runtime's ignore file to protect another runtime.

Manual prompt transfer is safest for exploratory runtimes. Copy only the
minimal prompt, source links, task packet, and validation checklist required for
the task, then record what was copied in the receipt or handoff.

For review-only local-model experiments, also record the model/provider,
endpoint boundary, expected capabilities, known caveats, and escalation
decision. If the endpoint boundary or capability is unknown, mark the run
`unknown` and avoid treating findings as complete evidence.
