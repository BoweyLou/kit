#!/usr/bin/env bash
set -euo pipefail

APP_NAME="KitCompanion"
BUNDLE_ID="com.boweylou.KitCompanion"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_BUNDLE="$ROOT_DIR/dist/$APP_NAME.app"
INSTALL_PATH="${KIT_COMPANION_INSTALL_PATH:-/Applications/$APP_NAME.app}"
RELAUNCH="${KIT_COMPANION_RELAUNCH:-auto}"

if [ "$(uname -s)" != "Darwin" ]; then
  echo "Kit Companion install is only supported on macOS." >&2
  exit 2
fi

if [ "${KIT_COMPANION_SKIP_BUILD:-0}" != "1" ]; then
  "$ROOT_DIR/script/build_macos_app.sh"
fi

if [ ! -d "$APP_BUNDLE" ]; then
  echo "Missing built app bundle: $APP_BUNDLE" >&2
  exit 2
fi

was_running=0
if /usr/bin/pgrep -x "$APP_NAME" >/dev/null 2>&1; then
  was_running=1
  /usr/bin/osascript -e "tell application id \"$BUNDLE_ID\" to quit" >/dev/null 2>&1 || true
  sleep 1
  /usr/bin/pkill -x "$APP_NAME" >/dev/null 2>&1 || true
fi

mkdir -p "$(dirname "$INSTALL_PATH")"
rm -rf "$INSTALL_PATH"
/usr/bin/ditto "$APP_BUNDLE" "$INSTALL_PATH"
/usr/bin/xattr -dr com.apple.quarantine "$INSTALL_PATH" >/dev/null 2>&1 || true
/usr/bin/codesign --verify --deep --strict "$INSTALL_PATH"

if [ "$RELAUNCH" = "1" ] || { [ "$RELAUNCH" = "auto" ] && [ "$was_running" = "1" ]; }; then
  /usr/bin/open "$INSTALL_PATH"
fi

version="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$INSTALL_PATH/Contents/Info.plist")"
echo "Installed $INSTALL_PATH ($version)"
