# Maintainer Guide

Use this page when changing kit itself.

## Ownership Map

| Area | Owns |
| --- | --- |
| `install.sh` | Global launcher installation and cached checkout setup. |
| `scripts/` | CLI, install/update logic, checks, reports, and helpers. |
| `templates/` | Files installed into target repos. |
| `workflows/` | Canonical prompt, persona, research, TDD, synthesis, and schema source. |
| `docs/` | Human, agent, maintainer, rollout, upgrade, and generated command docs. |
| `archive/agent-workflow-kit/` | Read-only legacy source and migration evidence. |

Do not put normal source work in `archive/agent-workflow-kit/`.

## Common Maintainer Checks

```bash
make docs-check
make docs-freshness
make workflow-source-check
make version-check
make test
```

Use a focused test first when the change is narrow, then broaden to `make test`
before committing behavior changes.

## Workflow Source Changes

When changing `workflows/` source:

```bash
make workflow-source-export
make workflow-source-check
make docs-freshness
```

Then run the relevant install/update tests so generated target surfaces are
covered.

## CLI Or Installer Changes

When changing public command behavior, install/update behavior, schemas,
profiles, generated docs, privacy/security policy, or version metadata:

```bash
make docs-freshness
make version-check
make test
```

Update `CHANGELOG.md` and `VERSION` when the change is part of a release scope.
For docs-only reshaping, a version bump is not required unless the published
operator contract changes.

## Documentation Shape

Keep `README.md` as the short front door.

Put detail here instead:

- capability inventory: [capabilities.md](capabilities.md)
- human operation: [human-guide.md](human-guide.md)
- agent operation: [agent-guide.md](agent-guide.md)
- command flags and JSON contracts: [cli-reference.md](cli-reference.md)
- update procedure: [upgrade-flow.md](upgrade-flow.md)
- source ownership: [agent-workflow-stack.md](agent-workflow-stack.md)
- v1/archive/rollback policy: [version-1-consolidation.md](version-1-consolidation.md)

## Release Boundary

Kit has one public repository, one installer, one CLI, and one
`VERSION`/`CHANGELOG.md` stream. The old `agent-workflow-kit` and
`repo-contract-kit` remotes are legacy/private/deprecated sources.

Do not create a second normal workflow-source repository or make target repos
clone workflow source at runtime.
