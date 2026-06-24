# ADR 0002: Managed Updates And Versioning

## Status

Accepted

## Context

The kit is installed into target repositories that may be private, offline,
hosted on old Bitbucket, or unable to run GitHub Actions. Once installed, those
repositories need a low-friction way to receive kit improvements without losing
local changes. The same repositories also need a simple version baseline so
agents can reason about behavior changes, changelog entries, and release impact.

## Decision

Use safe managed updates and local SemVer by default.

The kit publishes its own version in root `VERSION` and records that version,
the source ref, the computed `workflow-source` prompt snapshot ref/hash, the
selected preset, profiles, and managed file hashes in each target repository
under `.doc-contract-kit/`. Installs keep
`.doc-contract-kit/install.json` for compatibility and add
`.doc-contract-kit/manifest.json` as the managed-file source of truth. Both
metadata files carry `profile_config_schema_version` so future profile,
preset, runtime-adapter, or install metadata changes can be detected before an
update mutates target files.

Target repositories get local update entrypoints:

- `make kit-status`
- `make kit-status KIT=/path/to/kit`
- `make kit-migrate-config KIT=/path/to/kit`
- `make kit-update KIT=/path/to/kit`
- `make kit-refresh KIT=/path/to/kit`
- `make kit-explain`

When `KIT` is supplied, `kit-status` compares the installed kit and prompt
snapshot against the local checkout and reports whether an update is current or
available.

Updates only overwrite a managed file when the current target file still matches
the last installed hash. If a file was customized, the updater preserves it and
writes a proposed replacement plus a conflict report under
`.doc-contract-kit/updates/`.

`update-plan` is non-mutating and reports whether profile/config schema metadata
is current, missing, outdated, or blocked. When only metadata migration is
needed, `make kit-migrate-config` and `repo_contract_kit.py migrate-config`
apply the explicit `--metadata-only` path. That path updates only
`.doc-contract-kit/install.json` and `.doc-contract-kit/manifest.json`; it does
not rewrite target-owned files, managed files, or customized managed-file
conflict baselines.

The target repository owns its root `Makefile`. The kit-owned make command
surface is installed under `.doc-contract-kit/make/repo-contract.mk`, and the
root `Makefile` includes that fragment when the target wants kit commands. A
clean old kit-managed root `Makefile` can be migrated automatically to the
bridge; a customized root `Makefile` is preserved with a proposed bridge and
explicit merge guidance.

`kit-refresh` is a convenience wrapper for local kit checkouts. It refuses dirty
kit working trees, runs a fast-forward-only pull, prints the post-pull status,
and then delegates to the same conservative updater.

Agentic installs include a `versioning` profile. That profile creates
`VERSION`, `CHANGELOG.md`, `docs/versioning.md`, and local version commands when
missing. `VERSION` and `CHANGELOG.md` are target-owned after creation, so kit
updates never overwrite a project version history. Tags should use SemVer names
such as `v0.3.0` when a repository can use tags, but tags are not mandatory.

## Consequences

The default workflow remains local-only and host-agnostic. Agents can inspect
kit version, prompt snapshot identity, target repo version, and pending update
state without relying on hosted CI/CD or GitHub APIs.

The updater is intentionally conservative. Customized files require human or
agent review before adopting proposed replacements, which may make updates a
little slower but avoids destructive overwrites.
