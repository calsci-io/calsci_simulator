from __future__ import annotations

import sys
import time
from pathlib import Path


LCD_BYTES = 128 * 64 // 8
STATE_SIZE = 4 + LCD_BYTES


def _load_sim_ui():
    simulator_dir = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(simulator_dir))
    import sim_ui  # type: ignore

    return sim_ui


def _apply_state(sim_ui, payload: bytes):
    if len(payload) < STATE_SIZE or payload[0] != 1:
        return

    sim_ui.set_invert(bool(payload[1]))
    sim_ui.set_display_on(bool(payload[2]))
    sim_ui.set_all_points_on(bool(payload[3]))
    sim_ui.set_framebuffer(payload[4 : 4 + LCD_BYTES])
    sim_ui.render(force=True)


def _append_keys(key_path: Path, events):
    if not events:
        return

    with key_path.open("a", encoding="utf-8") as fh:
        for row, col in events:
            fh.write(f"{col},{row}\n")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: live_viewer.py <ipc_dir>", file=sys.stderr)
        return 2

    ipc_dir = Path(sys.argv[1])
    ipc_dir.mkdir(parents=True, exist_ok=True)

    state_path = ipc_dir / "display_state.bin"
    key_path = ipc_dir / "keys.txt"
    stop_path = ipc_dir / "stop"
    key_path.touch(exist_ok=True)

    sim_ui = _load_sim_ui()
    sim_ui.ensure_ui()

    last_sig = None

    while True:
        if stop_path.exists():
            return 0

        try:
            events = sim_ui.pop_pending_keys()
        except SystemExit:
            return 0

        _append_keys(key_path, events)

        try:
            stat = state_path.stat()
        except FileNotFoundError:
            sim_ui.render(force=False)
            time.sleep(0.01)
            continue

        sig = (stat.st_mtime_ns, stat.st_size)
        if sig != last_sig:
            try:
                payload = state_path.read_bytes()
            except OSError:
                payload = b""
            _apply_state(sim_ui, payload)
            last_sig = sig
        else:
            sim_ui.render(force=False)

        time.sleep(0.01)


if __name__ == "__main__":
    raise SystemExit(main())
