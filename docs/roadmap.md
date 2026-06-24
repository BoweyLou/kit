# Roadmap

The documentation contract remains the core use case, but the roadmap now
covers the broader local repository contract for agentic development.

## v0.1

- minimal templates
- basic install script
- basic documentation impact checker
- beginner-friendly docs

## v0.2

- upgrade script
- configurable path classification
- explicit no-docs-needed declaration support
- composable profiles and named presets
- installed profile receipt
- review-prompts and test-first profiles
- local-agentic profile for AmpCode, Codex, and other local agent tools
- local agent-instruction lint
- local docs-impact localization JSON
- safe-output schema for local agent review reports
- example repos with more realism
- installer tests

## v0.3

- root kit `VERSION` and `CHANGELOG.md`
- managed install manifest with per-file hashes
- safe local updater with conflict reports under `.doc-contract-kit/updates/`
- target-repo `kit-status` and `kit-update` commands
- default target-repo versioning profile for agentic installs
- `agent-start` kit/version context
- `agent-start` review-risk and trust-profile context
- `agent-run-review` manual/Amp read-only review runner artifacts
- task-packet prompt/schema bridge for repo backlog mirrors and external planning systems
- compatibility notes for existing `.doc-contract-kit/` install receipts
- consolidated workflow-source ownership under `workflows/`
- version 1 repository identity, archive policy, compatibility gate, and
  rollback contract under `docs/version-1-consolidation.md`
- generated docs integration
- broader executable docs checks
- stack-aware template profiles
- docs-only external planning and memory adapter examples
- benchmark fixtures for docs-impact false positives and review noise

## v0.4

- richer upgrade paths with an installed guided upgrade flow
- target-repo `kit-refresh` command for clean local checkout pull plus safe update
- repo scoring/freshness heuristics
- opt-in private-context profile with ignored local context templates and
  privacy warnings
- experimental docs-as-tests profile for declared local JSON OpenAPI operation checks
- optional CI adapters for teams that can use them
