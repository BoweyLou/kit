#!/usr/bin/env bash
set -euo pipefail

APP_NAME="KitCompanion"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
DMG_ROOT="$DIST_DIR/dmg-root"
VERSION="$(tr -d '[:space:]' <"$ROOT_DIR/VERSION")"
ARCH="${KIT_COMPANION_RELEASE_ARCH:-$(uname -m)}"
APP_BUNDLE="$DIST_DIR/$APP_NAME.app"
DMG_PATH="$DIST_DIR/$APP_NAME-$VERSION-macos-$ARCH.dmg"
SUMS_PATH="$DIST_DIR/SHA256SUMS"

"$ROOT_DIR/script/build_macos_app.sh"

rm -rf "$DMG_ROOT" "$DMG_PATH"
mkdir -p "$DMG_ROOT"
cp -R "$APP_BUNDLE" "$DMG_ROOT/"
ln -s /Applications "$DMG_ROOT/Applications"

/usr/bin/hdiutil create \
  -volname "$APP_NAME $VERSION" \
  -srcfolder "$DMG_ROOT" \
  -ov \
  -format UDZO \
  "$DMG_PATH"

(
  cd "$DIST_DIR"
  /usr/bin/shasum -a 256 "$(basename "$DMG_PATH")" >"$SUMS_PATH"
)

echo "Created $DMG_PATH"
echo "Wrote $SUMS_PATH"
