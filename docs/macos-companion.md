# Kit Companion for macOS

Kit Companion is an optional macOS menu-bar app for people who want a visible
local status surface for enrolled kit repos. The app is not required to install,
use, update, or operate kit.

The CLI remains the source of truth. Every workflow exposed by the app must
also remain available through terminal commands.

## What It Does

The companion app reads the same JSON contracts used by agents and scripts:

- `kit target dirty-report --json`
- `kit status --repo <repo> --json`
- `kit start --repo <repo> --no-update --json`
- `kit closeout-plan --repo <repo> --json`
- `kit update --all --dry-run --json`

The app shows registered targets, dirty repo counts, drift state, selected repo
closeout state, and copyable next commands.

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
current app version with the latest GitHub release and opens the release DMG
when the user chooses to download it.

## Safety Boundary

The app runs read-only commands in-app. It blocks mutating command flags such as
`--apply`, `--write`, `--write-sidecar`, and `--global`.

When a workflow needs a write, use the terminal. This keeps review, update, and
repo mutation behavior visible and consistent with the CLI.

## Build Locally

```bash
make macos-build
make macos-test
```

`make macos-test` currently performs a SwiftPM build check because the local
Command Line Tools environment used for this project does not provide XCTest.

The app defaults to `~/.local/bin/kit`. If the launcher lives elsewhere, set it
in Settings or launch with `KIT_COMPANION_KIT_PATH=/path/to/kit`.

## Private DMG

```bash
make macos-dmg
make macos-package-check
```

The DMG is written under `dist/` and uses ad hoc signing for local trusted-Mac
installs. It is not notarized in this private lane, so macOS may require
Control-click > Open or Privacy & Security > Open Anyway on first launch.
