#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SIMULATOR_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DEFAULT_MPY_FIRMWARE="/home/sobik/Lvgl Micropython/lvgl_integration/mpy_firmware"
MPY_FIRMWARE_DIR="${CALSCI_MPY_FIRMWARE:-$DEFAULT_MPY_FIRMWARE}"
MPY_BIN="$MPY_FIRMWARE_DIR/ports/unix/build-lvgl/micropython"
ENTRY="$SCRIPT_DIR/main.py"
BUILD_SCRIPT="$SCRIPT_DIR/build_real_lvgl.sh"
VIEWER_SCRIPT="$SCRIPT_DIR/live_viewer.py"
PYTHON_BIN="${CALSCI_SIM_PYTHON:-python3}"
IPC_DIR=""
VIEWER_PID=""

cleanup() {
  local status=$?

  if [[ -n "$IPC_DIR" ]]; then
    : > "$IPC_DIR/stop" 2>/dev/null || true
  fi

  if [[ -n "$VIEWER_PID" ]]; then
    kill "$VIEWER_PID" 2>/dev/null || true
    wait "$VIEWER_PID" 2>/dev/null || true
  fi

  if [[ -n "$IPC_DIR" ]]; then
    rm -rf "$IPC_DIR"
  fi

  exit "$status"
}

trap cleanup EXIT INT TERM

if [[ ! -x "$MPY_BIN" ]]; then
  if [[ "${CALSCI_AUTO_BUILD_LVGL:-0}" == "1" ]]; then
    "$BUILD_SCRIPT"
  else
    echo "LVGL unix binary not found at: $MPY_BIN" >&2
    echo "Build it with:" >&2
    echo "  CALSCI_MPY_FIRMWARE=\"$MPY_FIRMWARE_DIR\" $BUILD_SCRIPT" >&2
    echo "Or auto-build once by running:" >&2
    echo "  CALSCI_MPY_FIRMWARE=\"$MPY_FIRMWARE_DIR\" CALSCI_AUTO_BUILD_LVGL=1 $SIMULATOR_DIR/main_mpy_lvgl.sh" >&2
    exit 1
  fi
fi

if [[ "${CALSCI_HEADLESS:-0}" != "1" ]]; then
  IPC_DIR="$(mktemp -d "${TMPDIR:-/tmp}/calsci-sim.XXXXXX")"
  export CALSCI_SIM_IPC_DIR="$IPC_DIR"
  "$PYTHON_BIN" "$VIEWER_SCRIPT" "$IPC_DIR" &
  VIEWER_PID=$!
fi

"$MPY_BIN" "$ENTRY" "$@"
