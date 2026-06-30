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
- `kit update --all --dry-run --json`

The app shows registered targets, dirty repo counts, drift state, selected repo
closeout state, workflow checks, batch dry-run previews, and copyable next
commands.

The command browser is generated from `kit command-map --json`. It shows the
full global CLI surface, including agent-facing and Terminal-only commands, and
classifies each command into one of these app actions:

- Native: already shown in the target overview.
- Run: read-only JSON command that can run in the app.
- Preview: potentially mutating workflow with a safe app argument set such as
  `--dry-run` or `--no-update`.
- Terminal: command is visible and copyable, but execution belongs in a
  terminal.

This gives the app feature parity with the global CLI as a navigation and
status surface without making it a write-capable replacement for the CLI.

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

Automatic update checking does not silently replace the app. It compares the
current app version with the Sparkle appcast published in GitHub Releases. When
an app update is available, Sparkle verifies the update signature, downloads
the app archive, and replaces the installed app after user confirmation.

## Safety Boundary

The app runs read-only commands and explicit preview commands in-app. Preview
commands use CLI-supported no-write flags such as `--dry-run` and
`--no-update`. The runner blocks mutating command flags such as `--apply`,
`--write`, `--write-sidecar`, and `--global`.

When a workflow needs a write, use the terminal. This keeps review, update, and
repo mutation behavior visible and consistent with the CLI.

## Build Locally

```bash
make macos-build
make macos-test
```

`make macos-test` builds a small Swift check executable from the app's command
model, payload model, runner, and test harness source. The local Command Line
Tools environment used for this project does not provide XCTest or Swift
Testing, so this target uses `swiftc` assertions instead of `swift test`.

The app defaults to `~/.local/bin/kit`. If the launcher lives elsewhere, set it
in Settings or launch with `KIT_COMPANION_KIT_PATH=/path/to/kit`.

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
