# calsci_latest_itr_simulator

Thin desktop simulator for `calsci_latest_itr`.

This folder only provides hardware and MicroPython compatibility shims:
- display driver shim: `st7565.py`
- keypad + display UI surface: `sim_ui.py`
- MicroPython runtime shims: `machine.py`, `network.py`, `esp32.py`, `utime.py`, `urequests.py`, etc.

All app/runtime logic is imported and executed directly from `../calsci_latest_itr`.

## Run

```bash
cd calsci_latest_itr_simulator
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Run On MicroPython unix Port (Headless)

Use the dedicated unix runtime when you want CalSci core logic to execute under `mpy_firmware` constraints (no desktop UI).

```bash
cd /home/sobik/calsci_org
mpy_firmware/ports/unix/build-standard/micropython calsci_latest_itr_simulator/unix_port/main.py
```

If you need full LVGL (real binding, not stub), use the unix helper that mirrors the ESP32-S3 LVGL integration settings:

```bash
calsci_latest_itr_simulator/unix_port/build_real_lvgl.sh
mpy_firmware/ports/unix/build-lvgl/micropython calsci_latest_itr_simulator/unix_port/main.py
```

ESP32-S3 reference:
- Firmware build uses `USER_C_MODULES=<repo>/c_modules/micropython.cmake` (CMake flow).
- Unix port uses `USER_C_MODULES=../../lib` (Make flow) with the same LVGL tuning:
  `LV_CONF_PATH=../../lib/lv_binding_micropython/lv_conf.h` and `LV_CFLAGS=-DLV_COLOR_DEPTH=1`.

Shortcut:

```bash
calsci_latest_itr_simulator/main_mpy_lvgl.sh
```

Smoke test:

```bash
mpy_firmware/ports/unix/build-standard/micropython calsci_latest_itr_simulator/unix_port/main.py --smoke
```

## Controls

- Click calculator keys in the window.
- Optional keyboard shortcuts:
  - `Enter` -> `ok`
  - `Backspace` -> `back`
  - Arrow keys -> navigation keys
  - `Esc` -> `home`
  - `Ctrl+Q` -> quit

## Notes

- Paths like `/db/...` or `/apps/...` are remapped to `../calsci_latest_itr/db/...` and `../calsci_latest_itr/apps/...`.
- Some hardware/network-specific apps run in simulated/no-op mode where needed.
