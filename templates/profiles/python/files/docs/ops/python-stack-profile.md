# Python Stack Profile

This repo opted into the `python` repo-contract-kit profile.

The profile adds local Python hygiene guidance for agents and maintainers. It
does not create virtual environments, install packages, generate lockfiles,
choose a build backend, publish packages, or assume pytest, tox, nox, uv,
Poetry, or pip-tools.

## What To Inspect First

- `pyproject.toml`
- `setup.cfg`, `setup.py`, `requirements*.txt`, or `Pipfile`
- committed lockfiles: `uv.lock`, `poetry.lock`, `Pipfile.lock`, or
  `requirements.lock`
- test and lint config such as `pytest.ini`, `tox.ini`, `noxfile.py`,
  `ruff.toml`, `.ruff.toml`, `mypy.ini`, or `pyrightconfig.json`
- existing local docs for build, test, deploy, and release commands

## Agent Rules

- Inspect project config before running Python-specific commands.
- Prefer existing repo scripts, Make targets, or documented wrappers over
  global tooling assumptions.
- Do not install dependencies, create virtual environments, or rewrite lockfiles
  unless the human explicitly asks for that operation.
- Treat missing config as missing evidence, not as permission to invent a
  command.
- Keep repo-contract-kit docs checks separate from application test commands.

## Useful Local Checks

These are hints, not guaranteed commands. Run them only when dependencies and
configuration already exist.

```bash
python3 -m unittest discover
python3 -m pytest
python3 -m ruff check .
```

If the repo uses tox, nox, uv, Poetry, or a Makefile wrapper, prefer the
documented local command and avoid install/update commands unless requested.

## Machine-Readable Hints

The profile also installs:

```text
.agent-workflows/stack-profiles/python.json
```

That file is a local hint document for tools. It is not a package-manager
configuration file and should not be used to infer permission for environment,
network, dependency, or publishing operations.
