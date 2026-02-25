#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MPY_BIN="$ROOT_DIR/mpy_firmware/ports/unix/build-lvgl/micropython"
ENTRY="$ROOT_DIR/calsci_latest_itr_simulator/unix_port/main.py"
BUILD_SCRIPT="$ROOT_DIR/calsci_latest_itr_simulator/unix_port/build_real_lvgl.sh"

if [[ ! -x "$MPY_BIN" ]]; then
  if [[ "${CALSCI_AUTO_BUILD_LVGL:-0}" == "1" ]]; then
    "$BUILD_SCRIPT"
  else
    echo "LVGL unix binary not found at: $MPY_BIN" >&2
    echo "Build it with:" >&2
    echo "  $BUILD_SCRIPT" >&2
    echo "Or auto-build once by running:" >&2
    echo "  CALSCI_AUTO_BUILD_LVGL=1 $0" >&2
    exit 1
  fi
fi

exec "$MPY_BIN" "$ENTRY" "$@"
