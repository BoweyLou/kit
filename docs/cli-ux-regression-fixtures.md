# CLI UX regression fixtures

The CLI UX fixtures protect the wording and structure that humans and agents
depend on when using `kit`. They cover high-value command surfaces instead of
snapshotting every byte of output:

- top-level help scenario lanes
- concise parse-error recovery text
- `KIT_AGENT=1` parse-error JSON and no-write metadata
- `--no-input` prompt suppression
- command-map JSON shape
- compact `doctor` and `update --dry-run` summaries
- non-TTY `palette` fallback guidance
- generated CLI reference freshness

Run the fixture suite with:

```sh
make cli-ux-fixtures
```

or directly:

```sh
python3 -m unittest tests.test_cli_ux_fixtures
```

The manifest lives at `tests/fixtures/cli_ux/manifest.json`. Each case declares
the command arguments, expected exit code, and behavior-focused output checks.
Fixtures may create temporary git repositories, and the `installed_target`
fixture runs `kit setup` inside a temporary repository before executing the
case. The suite must not depend on the live checkout being clean or installed.

## Reviewing intentional changes

Treat a fixture failure as a CLI contract review point. If a wording or
structure change is intentional, update the fixture in the same change as the
CLI behavior and explain the reason in the PR summary. Keep assertions specific
enough to protect actionable phrases, recovery commands, JSON fields, and
write-safety promises. Do not replace a precise assertion with a broad substring
unless the user-facing contract itself became broader.
