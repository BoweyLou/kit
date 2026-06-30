#!/usr/bin/env bash
set -euo pipefail

APP_NAME="KitCompanion"
SPARKLE_ACCOUNT="${SPARKLE_ACCOUNT:-com.boweylou.KitCompanion}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
SPARKLE_DIR="$DIST_DIR/sparkle"
VERSION="$(tr -d '[:space:]' <"$ROOT_DIR/VERSION")"
ARCH="${KIT_COMPANION_RELEASE_ARCH:-$(uname -m)}"
APP_BUNDLE="$DIST_DIR/$APP_NAME.app"
ZIP_NAME="$APP_NAME-$VERSION-macos-$ARCH.zip"
ZIP_PATH="$SPARKLE_DIR/$ZIP_NAME"
APPCAST_PATH="$SPARKLE_DIR/KitCompanion-appcast.xml"
DOWNLOAD_URL_PREFIX="${SPARKLE_DOWNLOAD_URL_PREFIX:-https://github.com/BoweyLou/kit/releases/download/v$VERSION/}"

"$ROOT_DIR/script/build_macos_app.sh"

rm -rf "$SPARKLE_DIR"
mkdir -p "$SPARKLE_DIR"

/usr/bin/ditto -c -k --keepParent "$APP_BUNDLE" "$ZIP_PATH"
cat >"$SPARKLE_DIR/$APP_NAME-$VERSION-macos-$ARCH.md" <<EOF
# Kit Companion $VERSION

See the kit release notes for this version:
https://github.com/BoweyLou/kit/releases/tag/v$VERSION
EOF

GENERATE_APPCAST="$ROOT_DIR/macos/KitCompanion/.build/artifacts/sparkle/Sparkle/bin/generate_appcast"
if [ ! -x "$GENERATE_APPCAST" ]; then
  echo "Missing Sparkle generate_appcast tool. Run make macos-test first." >&2
  exit 1
fi

if [ -n "${SPARKLE_ED_PRIVATE_KEY:-}" ]; then
  /usr/bin/printf "%s" "$SPARKLE_ED_PRIVATE_KEY" | "$GENERATE_APPCAST" \
    --ed-key-file - \
    --download-url-prefix "$DOWNLOAD_URL_PREFIX" \
    --embed-release-notes \
    -o "$APPCAST_PATH" \
    "$SPARKLE_DIR"
else
  "$GENERATE_APPCAST" \
    --account "$SPARKLE_ACCOUNT" \
    --download-url-prefix "$DOWNLOAD_URL_PREFIX" \
    --embed-release-notes \
    -o "$APPCAST_PATH" \
    "$SPARKLE_DIR"
fi

(
  cd "$SPARKLE_DIR"
  /usr/bin/shasum -a 256 "$ZIP_NAME" "$(basename "$APPCAST_PATH")" >SHA256SUMS-sparkle
)

echo "Created $ZIP_PATH"
echo "Created $APPCAST_PATH"
echo "Wrote $SPARKLE_DIR/SHA256SUMS-sparkle"
