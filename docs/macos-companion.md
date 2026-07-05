# Kit Companion for macOS

Kit Companion is an optional macOS menu-bar app for people who want a visible
local status surface for enrolled kit repos. The app is not required to install,
use, update, or operate kit.

The CLI remains the source of truth. Every workflow exposed by the app must
also remain available through terminal commands.

## What It Does

The companion app reads the same JSON contracts used by agents and scripts:

- `kit command-map --json`
- `kit target dirty-report --json`
- `kit status --repo <repo> --json`
- `kit start --repo <repo> --no-update --json`
- `kit closeout-plan --repo <repo> --json`
- `kit closeout-fix --repo <repo> --apply --jsonl`
- `kit update --all --dry-run --json`
- `kit target import --root <selected-target> --apply --json`
- `kit target prune-missing --apply --json`
- `kit worktree prune --root <selected-target> --apply --json`
- `kit target update-all --apply --json`

The app opens to a selected-repo overview. The overview shows worktree status,
closeout state, kit drift, selected mode, one recommended action, closeout
blockers, copyable next commands, and collapsed technical activity for
closeout-fix jobs and update previews. The Batch tab can run dirty-repo guided
closeout jobs with a concurrency limit of two, and it exposes explicit
allowlisted apply buttons for target registry cleanup, clean-target updates,
and clean disposable worktree pruning. The header keeps target actions, batch
previews, and app update checks separate so a target update dry-run is not
confused with a Sparkle app update check.

The command browser is generated from `kit command-map --json`. It groups the
global CLI surface into scoped views:

- Recommended: common operator checks and native app surfaces.
- Read-only: JSON commands that can run in the app without write flags.
- Previews: workflows that the app can run only with no-write flags such as
  `--dry-run` or `--no-update`.
- Terminal: commands visible for copy or Terminal handoff.
- Agent: agent-facing commands kept out of the recommended operator view.

Each command still has one app action classification:

- Native: already shown in the target overview.
- Run: read-only JSON command that can run in the app.
- Preview: potentially mutating workflow with a safe app argument set such as
  `--dry-run` or `--no-update`.
- Terminal: command is visible and copyable, but execution belongs in a
  terminal.

This gives the app feature parity with the global CLI as a navigation and
status surface without making the command browser a write-capable replacement
for the CLI.

## Settings

Kit Companion stores app-only preferences in macOS user defaults:

- `kitBinaryPath`: path to the local `kit` launcher. The default is
  `~/.local/bin/kit`.
- `automaticallyCheckForUpdates`: whether the app checks the latest GitHub
  release when it starts. The default is enabled.

Launch at Login is managed through macOS login item registration. It is
optional and only starts the companion app; it does not run kit updates or
mutate target repos. The app should be installed in `/Applications` before
enabling Launch at Login for normal use.

If macOS reports that the login item needs approval, the Settings window shows
that state and includes an Open Login Items button. Approve Kit Companion in
System Settings > General > Login Items, then return to the app; the setting
refreshes when the app becomes active again.

Automatic update checking does not silently replace the app. It compares the
current app version with the Sparkle appcast published in GitHub Releases. When
an app update is available, Sparkle verifies the update signature, downloads
the app archive, and replaces the installed app after user confirmation.

## Safety Boundary

The app runs read-only commands and explicit preview commands in-app. Preview
commands use CLI-supported no-write flags such as `--dry-run` and
`--no-update`. The runner blocks mutating command flags such as `--apply`,
`--write`, `--write-sidecar`, and `--global`.

Guided Closeout and Batch Maintenance are the only write-capable app
exceptions. Guided Closeout is shown from the selected target overview when the
repo is dirty or closeout has blockers, and requires confirmation before
starting. The Batch tab can run guided closeout for multiple dirty targets with
at most two concurrent jobs. Each repo gets its own job card, streamed events,
result payload, receipt path, and blocker explanations.

The closeout runner accepts exactly:

```bash
kit closeout-fix --repo <selected-target> --apply --jsonl
```

That runner rejects custom agent commands and arbitrary mutating command
shapes. A blocked guided closeout is rendered as a workflow result with a human
reason and next action, not as a generic process error. The generic command
browser continues to run `closeout-fix` preview-only.

Batch Maintenance uses a second allowlisted write runner for exactly:

```bash
kit target import --root <selected-target> --apply --json
kit target prune-missing --apply --json
kit worktree prune --root <selected-target> --apply --json
kit target update-all --apply --json
kit target closeout-all --apply --policy gated --json
```

These actions still require app confirmation. `target update-all --apply`
relies on the CLI's clean-target gate and skips dirty, missing, or
no-longer-enrolled targets. `target closeout-all --apply --policy gated`
reads only the kit target registry and leaves active, ambiguous, or
default-branch-integration work as `LEFT-UNFINISHED` or `NEEDS-REVIEW`.
`worktree prune --apply` removes only eligible clean linked worktrees under
agent-worktrees paths. Setup, install, global tool updates, self updates,
custom closeout agents, arbitrary target writes, and `--write-sidecar` commands
remain Terminal handoffs.

## Build Locally

```bash
make macos-build
make macos-install
make macos-test
```

`make macos-test` builds a small Swift check executable from the app's command
model, payload model, runner, and test harness source. The local Command Line
Tools environment used for this project does not provide XCTest or Swift
Testing, so this target uses `swiftc` assertions instead of `swift test`.

The app defaults to `~/.local/bin/kit`. If the launcher lives elsewhere, set it
in Settings or launch with `KIT_COMPANION_KIT_PATH=/path/to/kit`.

`make macos-install` rebuilds the app, replaces the installed bundle at
`/Applications/KitCompanion.app` by default, and relaunches it when it was
already running. Set `KIT_COMPANION_INSTALL_PATH=~/Applications/KitCompanion.app`
to use a per-user install path.

When `kit update --global` or `kit self update` runs on macOS, the updater also
refreshes the installed Kit Companion app if it finds the bundle in
`/Applications` or `~/Applications`. Machines without the optional app skip that
step. Set `KIT_COMPANION_UPDATE_ON_GLOBAL_UPDATE=0` to disable the automatic app
refresh for one global update.

When launched from Finder or Login Items, the app supplies a stable command
search path that prefers Homebrew and Python framework locations before
macOS's system paths. This keeps the kit launcher from falling back to an older
system Python just because the app was not started from a terminal shell.

## Private DMG

```bash
make macos-dmg
make macos-sparkle
make macos-package-check
```

The DMG is written under `dist/` and uses ad hoc signing for local trusted-Mac
installs. It is not notarized in this private lane, so macOS may require
Control-click > Open or Privacy & Security > Open Anyway on first launch.

Sparkle update assets are written under `dist/sparkle/`:

- `KitCompanion-<version>-macos-<arch>.zip`
- `KitCompanion-appcast.xml`
- `SHA256SUMS-sparkle`

The Sparkle appcast is signed with the local Keychain item for
`com.boweylou.KitCompanion` by default. Automation can instead pass the private
EdDSA key through `SPARKLE_ED_PRIVATE_KEY`; do not commit that private key.
