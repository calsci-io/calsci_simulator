#!/usr/bin/env bash
set -euo pipefail

# ESP32-S3 reference (from your firmware flow):
#   USER_C_MODULES=<repo>/c_modules/micropython.cmake  (CMake path)
# Unix Make-port equivalent:
#   USER_C_MODULES=../../lib                            (Make path)
# Keep LVGL flags aligned with your ESP32-S3 integration defaults.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEFAULT_MPY_FIRMWARE="/home/sobik/Lvgl Micropython/lvgl_integration/mpy_firmware"
MPY_FIRMWARE_DIR="${CALSCI_MPY_FIRMWARE:-$DEFAULT_MPY_FIRMWARE}"
JOBS="${JOBS:-$(nproc 2>/dev/null || echo 4)}"

if [[ ! -d "$MPY_FIRMWARE_DIR/ports/unix" ]]; then
  echo "mpy_firmware unix port not found at: $MPY_FIRMWARE_DIR/ports/unix" >&2
  echo "Set CALSCI_MPY_FIRMWARE to the correct mpy_firmware root if needed." >&2
  exit 1
fi

exec make -C "$MPY_FIRMWARE_DIR/ports/unix" -j"$JOBS" \
  BUILD=build-lvgl \
  USER_C_MODULES=../../lib \
  LV_CONF_PATH=../../lib/lv_binding_micropython/lv_conf.h \
  LV_CFLAGS=-DLV_COLOR_DEPTH=1 \
  MICROPY_PY_SSL=0 MICROPY_SSL_MBEDTLS=0 MICROPY_SSL_AXTLS=0 \
  MICROPY_PY_HASHLIB=0 MICROPY_PY_CRYPTOLIB=0 MICROPY_PY_BTREE=0 MICROPY_PY_FFI=0
