# Runtime Adapters

Runtime adapters are optional, managed instruction files for tools that do not
read `AGENTS.md` directly. They are deliberately thin route maps, not a second
source of prompt truth.

Supported adapters:

| Adapter | Installed file | Purpose |
| --- | --- | --- |
| `claude-code` | `CLAUDE.md` | Routes Claude Code to `AGENTS.md`, `REVIEW.md`, and the installed workflow docs. |
| `github-copilot` | `.github/copilot-instructions.md` | Routes GitHub Copilot to the same repo-local guardrails. |

Claude Code documents project-level `CLAUDE.md` files for persistent project
instructions and recommends importing `AGENTS.md` when a repo already uses that
file. GitHub Copilot documents repository custom instructions at
`.github/copilot-instructions.md`. The kit adapter files follow those runtime
paths while keeping repo-specific rules in `AGENTS.md` and scoped docs.

References:

- [Claude Code memory docs](https://code.claude.com/docs/en/memory)
- [GitHub Copilot repository instructions docs](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions)

## Install

Adapters are not installed by default. Select them explicitly:

```bash
python3 scripts/install.py /path/to/target/repo --preset agentic --runtime-adapters claude-code,github-copilot
```

You can also repeat the singular flag:

```bash
python3 scripts/install.py /path/to/target/repo --preset agentic --runtime-adapter claude-code --runtime-adapter github-copilot
```

## Update

Existing installs keep the adapter list recorded in
`.doc-contract-kit/install.json`. To add or change adapters during a safe kit
update:

```bash
kit update --runtime-adapters claude-code,github-copilot
```

Or use the lower-level script:

```bash
python3 /path/to/kit/scripts/update.py "$(pwd)" --apply --runtime-adapters claude-code,github-copilot
```

Use `--runtime-adapters none` to clear the explicit adapter selection on an
update. The update remains managed and explicit; it does not delete target-owned
custom files outside the selected managed entries.

## Update Safety

Selected adapter files are recorded in `.doc-contract-kit/manifest.json` with
their source hash, installed hash, owner, and `runtime_adapter` name. Clean
managed adapters update automatically. Customized adapters are preserved, and a
proposed replacement plus update report is written under
`.doc-contract-kit/updates/`.

`make kit-status` prints the selected runtime adapters and includes adapter
files in the normal managed-file cleanliness check.
