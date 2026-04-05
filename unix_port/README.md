# unix_port

Run `calsci_latest_itr` core logic under the real MicroPython unix interpreter from `mpy_firmware`, without desktop UI rendering.

## What this does

- Uses `mpy_firmware/ports/unix/build-standard/micropython` as the runtime.
- Loads apps/modules directly from the simulator repo's `../calsci_latest_itr` submodule.
- Provides headless hardware shims (`machine`, `st7565`, `network`, `esp32`, `espnow`, etc.).
- Maps absolute firmware paths (for example `/db/...`, `/apps/...`, `/database/...`, `/certs/...`) into local workspace paths.

## Build unix MicroPython (if needed)

From repo root:

```bash
make -C mpy_firmware/mpy-cross -j4
make -C mpy_firmware/ports/unix -j4 \
  MICROPY_PY_SSL=0 MICROPY_SSL_MBEDTLS=0 MICROPY_SSL_AXTLS=0 \
  MICROPY_PY_HASHLIB=0 MICROPY_PY_CRYPTOLIB=0 MICROPY_PY_BTREE=0 MICROPY_PY_FFI=0
```

## Build unix MicroPython with full LVGL

This enables the real `lvgl` module from `mpy_firmware/lib/lv_binding_micropython`:

```bash
/home/sobik/calsci_simulator/unix_port/build_real_lvgl.sh
```

ESP32-S3 reference mapping:
- ESP32 build path uses CMake + `USER_C_MODULES=<repo>/c_modules/micropython.cmake`.
- Unix build path uses Make + `USER_C_MODULES=../../lib`.
- Both use LVGL settings equivalent to your firmware setup:
  `LV_CONF_PATH=../../lib/lv_binding_micropython/lv_conf.h` and `LV_CFLAGS=-DLV_COLOR_DEPTH=1`.
- Default firmware root is `/home/sobik/Lvgl Micropython/lvgl_integration/mpy_firmware`.
  Override it with `CALSCI_MPY_FIRMWARE=/path/to/mpy_firmware` if that changes.

## Run

From repo root:

```bash
/home/sobik/Lvgl Micropython/lvgl_integration/mpy_firmware/ports/unix/build-standard/micropython /home/sobik/calsci_simulator/unix_port/main.py
```

Run with full LVGL enabled:

```bash
/home/sobik/Lvgl Micropython/lvgl_integration/mpy_firmware/ports/unix/build-lvgl/micropython /home/sobik/calsci_simulator/unix_port/main.py
```

Or with helper script:

```bash
/home/sobik/calsci_simulator/unix_port/run_real_lvgl.sh
```

The helper script starts a companion desktop viewer by default so you can see the unix-port framebuffer.
Use `CALSCI_HEADLESS=1` to keep it headless.

Optional:

- Smoke test (imports core modules and exits):

```bash
/home/sobik/Lvgl Micropython/lvgl_integration/mpy_firmware/ports/unix/build-standard/micropython /home/sobik/calsci_simulator/unix_port/main.py --smoke
```

- Skip boot script and run only `calsci_latest_itr/main.py`:

```bash
/home/sobik/Lvgl Micropython/lvgl_integration/mpy_firmware/ports/unix/build-standard/micropython /home/sobik/calsci_simulator/unix_port/main.py --skip-boot
```

## Notes

- This mode is intentionally headless: no desktop calculator window and no click sound.
- `run_real_lvgl.sh` is the exception: it launches a desktop viewer that mirrors the unix-port framebuffer.
- `machine` keypad queue helper exists for automated tests:
  - `import machine`
  - `machine.queue_key(col, row)`
- Desktop `python /home/sobik/calsci_simulator/main.py` uses CPython and LVGL stub.
  Use `build-lvgl/micropython` if you need complete LVGL APIs.
