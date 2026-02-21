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
