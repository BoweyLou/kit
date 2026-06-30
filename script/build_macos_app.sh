#!/usr/bin/env bash
set -euo pipefail

APP_NAME="KitCompanion"
BUNDLE_ID="com.boweylou.KitCompanion"
MIN_SYSTEM_VERSION="14.0"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MACOS_DIR="$ROOT_DIR/macos/KitCompanion"
DIST_DIR="$ROOT_DIR/dist"
APP_BUNDLE="$DIST_DIR/$APP_NAME.app"
APP_CONTENTS="$APP_BUNDLE/Contents"
APP_MACOS="$APP_CONTENTS/MacOS"
APP_FRAMEWORKS="$APP_CONTENTS/Frameworks"
APP_RESOURCES="$APP_CONTENTS/Resources"
APP_BINARY="$APP_MACOS/$APP_NAME"
INFO_PLIST="$APP_CONTENTS/Info.plist"
VERSION="$(tr -d '[:space:]' <"$ROOT_DIR/VERSION")"
SPARKLE_PUBLIC_ED_KEY="of+DApGIVB8nkma7rnPbx6CCPTGV6Eta+BBiI7NjYng="
SPARKLE_FEED_URL="https://github.com/BoweyLou/kit/releases/latest/download/KitCompanion-appcast.xml"

swift build --package-path "$MACOS_DIR" -c release
BUILD_DIR="$(swift build --package-path "$MACOS_DIR" -c release --show-bin-path | tail -1)"
BUILD_BINARY="$BUILD_DIR/$APP_NAME"
SPARKLE_FRAMEWORK="$BUILD_DIR/Sparkle.framework"

rm -rf "$APP_BUNDLE"
mkdir -p "$APP_MACOS" "$APP_FRAMEWORKS" "$APP_RESOURCES"
cp "$BUILD_BINARY" "$APP_BINARY"
chmod +x "$APP_BINARY"
if [ -d "$SPARKLE_FRAMEWORK" ]; then
  /usr/bin/ditto "$SPARKLE_FRAMEWORK" "$APP_FRAMEWORKS/Sparkle.framework"
fi
if ! /usr/bin/otool -l "$APP_BINARY" | /usr/bin/grep -q "@executable_path/../Frameworks"; then
  /usr/bin/install_name_tool -add_rpath "@executable_path/../Frameworks" "$APP_BINARY"
fi
"$ROOT_DIR/script/generate_macos_icons.py" "$APP_RESOURCES"

cat >"$INFO_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>$APP_NAME</string>
  <key>CFBundleIdentifier</key>
  <string>$BUNDLE_ID</string>
  <key>CFBundleName</key>
  <string>$APP_NAME</string>
  <key>CFBundleDisplayName</key>
  <string>Kit Companion</string>
  <key>CFBundleIconFile</key>
  <string>AppIcon</string>
  <key>CFBundleShortVersionString</key>
  <string>$VERSION</string>
  <key>CFBundleVersion</key>
  <string>$VERSION</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>LSMinimumSystemVersion</key>
  <string>$MIN_SYSTEM_VERSION</string>
  <key>LSUIElement</key>
  <true/>
  <key>NSPrincipalClass</key>
  <string>NSApplication</string>
  <key>SUFeedURL</key>
  <string>$SPARKLE_FEED_URL</string>
  <key>SUPublicEDKey</key>
  <string>$SPARKLE_PUBLIC_ED_KEY</string>
  <key>SUEnableAutomaticChecks</key>
  <true/>
</dict>
</plist>
PLIST

/usr/bin/codesign --force --deep --sign - "$APP_BUNDLE"

echo "Built $APP_BUNDLE"
