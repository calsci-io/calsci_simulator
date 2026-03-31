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

## Build Standalone Ubuntu Bundle

Build a PyInstaller `--onedir` bundle that includes the simulator, Python runtime,
and the sibling `calsci_latest_itr` app tree:

```bash
cd calsci_latest_itr_simulator
pyinstaller --clean --noconfirm --distpath dist --workpath build calsci_simulator_onedir.spec
```

The runnable executable is created at:

```bash
dist/calsci_simulator/calsci_simulator
```

Copy the whole `dist/calsci_simulator/` folder to the target Ubuntu machine and run
the `calsci_simulator` executable from there.

If you want the packaged simulator to use a different `calsci_latest_itr` checkout
without rebuilding, either:

```bash
CALSCI_APP_DIR=/path/to/calsci_latest_itr ./dist/calsci_simulator/calsci_simulator
```

or place a `calsci_latest_itr/` folder next to the executable. In a PyInstaller
bundle, that external folder is preferred over the bundled copy.

## Run On MicroPython unix Port (Headless)

Use the dedicated unix runtime when you want CalSci core logic to execute under `mpy_firmware` constraints (no desktop UI).

```bash
/home/sobik/Lvgl Micropython/lvgl_integration/mpy_firmware/ports/unix/build-standard/micropython /home/sobik/calsci_simulator/unix_port/main.py
```

If you need full LVGL (real binding, not stub), use the unix helper that mirrors the ESP32-S3 LVGL integration settings:

```bash
/home/sobik/calsci_simulator/unix_port/build_real_lvgl.sh
/home/sobik/Lvgl Micropython/lvgl_integration/mpy_firmware/ports/unix/build-lvgl/micropython /home/sobik/calsci_simulator/unix_port/main.py
```

ESP32-S3 reference:
- Firmware build uses `USER_C_MODULES=<repo>/c_modules/micropython.cmake` (CMake flow).
- Unix port uses `USER_C_MODULES=../../lib` (Make flow) with the same LVGL tuning:
  `LV_CONF_PATH=../../lib/lv_binding_micropython/lv_conf.h` and `LV_CFLAGS=-DLV_COLOR_DEPTH=1`.
- Override the default firmware path if needed with `CALSCI_MPY_FIRMWARE=/path/to/mpy_firmware`.

Shortcut:

```bash
/home/sobik/calsci_simulator/main_mpy_lvgl.sh
```

This wrapper now opens the desktop simulator window while the real unix-port LVGL runtime is running.
Use `CALSCI_HEADLESS=1` if you want the old headless behavior.

Smoke test:

```bash
/home/sobik/Lvgl Micropython/lvgl_integration/mpy_firmware/ports/unix/build-standard/micropython /home/sobik/calsci_simulator/unix_port/main.py --smoke
```

## Controls

- Click calculator keys in the window.
- Optional keyboard shortcuts:
  - `F5` -> reload the simulator
  - `Enter` -> `ok`
  - `Backspace` -> `back`
  - `Delete` -> `nav_b`
  - Arrow keys -> navigation keys
  - `Ctrl+Left` -> `back`
  - `Ctrl+A` -> `alpha`
  - `Ctrl+B` -> `beta`
  - `Ctrl+H` -> `home`
  - `Ctrl+L` -> `lock`
  - `0-9`, `.,()+-/*` -> matching calculator keys
  - `F1`, `F2`, `F3`, `F4`, `F6` -> matching calculator keys
  - `S` -> save a display screenshot
  - `V` -> start/stop display video recording
  - `Esc` -> `home`
  - `Ctrl+Q` -> quit

## Notes

- Paths like `/db/...` or `/apps/...` are remapped to `../calsci_latest_itr/db/...` and `../calsci_latest_itr/apps/...`.
- Some hardware/network-specific apps run in simulated/no-op mode where needed.
- Screenshots are saved in `../simulator_screen_shots`, and display recordings are saved in `../simulator_videos`.
- Display recording shells out to `ffmpeg`, so it needs to be available on `PATH`.
