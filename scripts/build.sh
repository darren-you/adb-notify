#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
VERSION="$(sed -n 's/^version=//p' "$ROOT_DIR/module/module.prop" | head -n 1)"
OUT_DIR="$ROOT_DIR/dist"
OUT_FILE="$OUT_DIR/usb-adb-notify-toggle-v$VERSION.zip"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

(
  cd "$ROOT_DIR/module"
  zip -r -9 "$OUT_FILE" .
)

if command -v shasum >/dev/null 2>&1; then
  shasum -a 256 "$OUT_FILE"
else
  sha256sum "$OUT_FILE"
fi
