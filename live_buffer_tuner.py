import os
import random
import select
import sys
import termios
import time
import tty
from pathlib import Path


SIM_DIR = Path("/home/sobik/calsci_simulator")
CALSCI_DIR = Path("/home/sobik/calsci_latest_itr")
LIB_DIR = CALSCI_DIR / "lib"

ordered_paths = [str(SIM_DIR), str(CALSCI_DIR), str(LIB_DIR)]
for path in ordered_paths:
    if path in sys.path:
        sys.path.remove(path)
sys.path[:0] = ordered_paths

from compat import install_compat


install_compat(calsci_dir=CALSCI_DIR, simulator_dir=SIM_DIR)
os.chdir(CALSCI_DIR)

import sim_ui
import st7565
from data_modules.object_handler import form, form_refresh
from process_modules import form_buffer_uploader as fbu


FOCUS_ORDER = [0, 2, 4, 5]
FOCUS_NAMES = ["Link", "Start Input", "Steps Input", "Run Button"]
KEY_WINDOW = 18
REFRESH_INTERVAL = 0.08
AUTO_CYCLE_SECS = 1.2
VALUE_MIN = 0
VALUE_MAX = 255
SAMPLE_CASES = [
    {
        "name": "mixed long",
        "inp_0": "X12345Y7890ABCD ",
        "inp_1": "9876543210 steps 42 ",
    },
    {
        "name": "numeric heavy",
        "inp_0": "1029384756657483 ",
        "inp_1": "12345678901234567890 ",
    },
    {
        "name": "short labels",
        "inp_0": "Start 12 ",
        "inp_1": "42 ",
    },
]


class RawTerminal:
    def __init__(self, stream):
        self.stream = stream
        self.output = sys.stdout
        self.fd = stream.fileno()
        self._attrs = None

    def __enter__(self):
        self._attrs = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._attrs is not None:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self._attrs)
        self.output.write("\x1b[?25h")
        self.output.flush()


def build_random_case():
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123456789"
    words = ["steps", "calc", "buffer", "mono", "run", "ui", "field"]
    prefix = random.choice(words).upper()[:4]
    middle = "".join(random.choice(alphabet + digits) for _ in range(10))
    numeric = "".join(random.choice(digits) for _ in range(16))
    return {
        "name": "random",
        "inp_0": f"{prefix}-{middle} ",
        "inp_1": f"{numeric} {random.choice(words)} ",
    }


def capture_form_state():
    return {
        "ui_style": getattr(form, "ui_style", "classic"),
        "focus_inputs_only": getattr(form, "focus_inputs_only", False),
        "blink_cursor": getattr(form, "blink_cursor", False),
        "title": getattr(form, "title", ""),
        "input_cols": getattr(form, "input_cols", 19),
        "form_list": list(getattr(form, "form_list", [])),
        "input_list": dict(getattr(form, "input_list", {})),
        "menu_cursor": getattr(form, "menu_cursor", 0),
    }


def restore_form_state(previous):
    form.ui_style = previous["ui_style"]
    form.focus_inputs_only = previous["focus_inputs_only"]
    form.blink_cursor = previous["blink_cursor"]
    form.title = previous["title"]
    form.input_cols = previous["input_cols"]
    form.form_list = previous["form_list"]
    form.input_list = previous["input_list"]
    form.menu_cursor = previous["menu_cursor"]
    form.update()
    try:
        form_refresh.refresh(force=True)
    except Exception:
        pass


def configure_form(sample):
    form.ui_style = "buffer"
    form.focus_inputs_only = False
    form.blink_cursor = True
    form.title = ""
    form.input_cols = 8
    form.input_list = {
        "inp_0": sample["inp_0"],
        "inp_1": sample["inp_1"],
    }
    form.form_list = [
        "@link Select Function",
        "@input_h Start",
        "inp_0",
        "@input_v Steps",
        "inp_1",
        "@button:center Run",
    ]
    form.update()


def set_focus(focus_index):
    focus_index = max(0, min(focus_index, len(FOCUS_ORDER) - 1))
    form.menu_cursor = FOCUS_ORDER[focus_index]
    try:
        form._sync_input_view(prefer_end=False)
    except Exception:
        pass
    form_refresh.refresh(force=True)
    return focus_index


def current_tuning():
    return dict(fbu.current_compact_tuning())


def apply_value(key, new_value):
    new_value = max(VALUE_MIN, min(VALUE_MAX, int(new_value)))
    fbu.apply_compact_tuning({key: new_value})
    form_refresh.refresh(force=True)
    return new_value


def reset_defaults():
    fbu.apply_compact_tuning(dict(fbu.COMPACT_TUNE_DEFAULTS))
    form_refresh.refresh(force=True)


def reload_saved():
    changed = fbu.load_compact_tuning()
    form_refresh.refresh(force=True)
    return changed


def read_key(timeout=0.0):
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if not ready:
        return None

    first = os.read(sys.stdin.fileno(), 1)
    if first == b"\x1b":
        if select.select([sys.stdin], [], [], 0.002)[0]:
            second = os.read(sys.stdin.fileno(), 1)
            if second == b"[" and select.select([sys.stdin], [], [], 0.002)[0]:
                third = os.read(sys.stdin.fileno(), 1)
                return {
                    b"A": "UP",
                    b"B": "DOWN",
                    b"C": "RIGHT",
                    b"D": "LEFT",
                }.get(third, "ESC")
        return "ESC"

    try:
        return first.decode("utf-8")
    except Exception:
        return None


def dirty_count(values):
    defaults = getattr(fbu, "COMPACT_TUNE_DEFAULTS", {})
    count = 0
    for key, value in values.items():
        if defaults.get(key) != value:
            count += 1
    return count


def render_screen(
    values,
    selected_index,
    focus_index,
    auto_cycle,
    sample_name,
    status,
):
    keys = list(fbu.COMPACT_TUNE_KEYS)
    selected_index = max(0, min(selected_index, len(keys) - 1))
    selected_key = keys[selected_index]
    defaults = getattr(fbu, "COMPACT_TUNE_DEFAULTS", {})
    saved_exists = os.path.exists(fbu.COMPACT_TUNE_FILE)

    window_start = max(0, selected_index - KEY_WINDOW // 2)
    window_end = min(len(keys), window_start + KEY_WINDOW)
    window_start = max(0, window_end - KEY_WINDOW)

    lines = [
        "\x1b[2J\x1b[H\x1b[?25l",
        "CalSci Buffer Live Tuner",
        "",
        "Preview: 1 Link | 2 Start | 3 Steps | 4 Run | current: "
        + FOCUS_NAMES[focus_index],
        "Control: j/k or arrows move | h/l +/-1 | H/L +/-5 | [/ ] jump 10",
        "Actions: a auto-cycle | c preset sample | x random sample | s save | r reload | d defaults | q quit",
        "Sample: " + sample_name,
        "Tuning file: " + fbu.COMPACT_TUNE_FILE,
        "Saved file present: " + ("yes" if saved_exists else "no"),
        "Changed from defaults: " + str(dirty_count(values)),
        "Auto-cycle: " + ("on" if auto_cycle else "off"),
        "Status: " + status,
        "",
        "  Key".ljust(38) + "Now".rjust(6) + "  Def".rjust(6) + "  Delta".rjust(8),
        "  " + "-" * 56,
    ]

    for index in range(window_start, window_end):
        key = keys[index]
        now_value = int(values.get(key, 0))
        default_value = int(defaults.get(key, 0))
        delta = now_value - default_value
        marker = ">" if index == selected_index else " "
        lines.append(
            f"{marker} {key:<35}{now_value:>7}{default_value:>7}{delta:>8}"
        )

    lines.extend(
        [
            "",
            "Selected: "
            + selected_key
            + " = "
            + str(values[selected_key])
            + " | default "
            + str(defaults.get(selected_key, 0)),
        ]
    )
    sys.stdout.write("\n".join(lines))
    sys.stdout.flush()


def print_line_help():
    print("Live tuner command mode")
    print("Commands: j k h l H L [ ] 1 2 3 4 a c x s r d q")
    print("Also: up down left right focus 1-4 set KEY VALUE save reload defaults show help quit")


def print_line_status(session, keys):
    values = current_tuning()
    selected_key = keys[session["selected_index"]]
    print(
        "Selected:",
        selected_key,
        "=",
        values[selected_key],
        "| focus:",
        FOCUS_NAMES[session["focus_index"]],
        "| sample:",
        session["sample"]["name"],
        "| changed:",
        dirty_count(values),
    )
    print("Status:", session["status"])


def init_session():
    sample = dict(SAMPLE_CASES[0])
    configure_form(sample)
    return {
        "sample": sample,
        "sample_index": 0,
        "focus_index": set_focus(0),
        "selected_index": 0,
        "auto_cycle": False,
        "next_cycle_at": time.monotonic() + AUTO_CYCLE_SECS,
        "status": "Ready. Adjust any constant and the preview will refresh live.",
    }


def tick_preview(session, last_refresh):
    now = time.monotonic()
    if session["auto_cycle"] and now >= session["next_cycle_at"]:
        session["focus_index"] = set_focus((session["focus_index"] + 1) % len(FOCUS_ORDER))
        session["next_cycle_at"] = now + AUTO_CYCLE_SECS

    if now - last_refresh >= REFRESH_INTERVAL:
        try:
            form_refresh.idle()
        except Exception:
            pass
        try:
            form_refresh.refresh(force=True)
        except Exception:
            pass
        last_refresh = now

    try:
        sim_ui.poll_events()
    except SystemExit:
        session["status"] = "Preview window closed."
        return last_refresh, False
    return last_refresh, True


def apply_command(command, session, keys):
    command = str(command or "").strip()
    if command == "":
        session["status"] = "No command entered."
        return True

    values = current_tuning()
    selected_key = keys[session["selected_index"]]
    now = time.monotonic()

    if command in ("\x03", "q", "quit", "exit"):
        session["status"] = "Exiting tuner."
        return False
    if command in ("j", "down", "next"):
        session["selected_index"] = min(len(keys) - 1, session["selected_index"] + 1)
        session["status"] = "Selected " + keys[session["selected_index"]]
        return True
    if command in ("k", "up", "prev", "previous"):
        session["selected_index"] = max(0, session["selected_index"] - 1)
        session["status"] = "Selected " + keys[session["selected_index"]]
        return True
    if command in ("[", "pageup"):
        session["selected_index"] = max(0, session["selected_index"] - 10)
        session["status"] = "Selected " + keys[session["selected_index"]]
        return True
    if command in ("]", "pagedown"):
        session["selected_index"] = min(len(keys) - 1, session["selected_index"] + 10)
        session["status"] = "Selected " + keys[session["selected_index"]]
        return True
    if command in ("h", "left", "-", "dec"):
        new_value = apply_value(selected_key, values[selected_key] - 1)
        session["status"] = selected_key + " -> " + str(new_value)
        return True
    if command in ("l", "right", "+", "inc", "="):
        new_value = apply_value(selected_key, values[selected_key] + 1)
        session["status"] = selected_key + " -> " + str(new_value)
        return True
    if command in ("H", "--", "dec5"):
        new_value = apply_value(selected_key, values[selected_key] - 5)
        session["status"] = selected_key + " -> " + str(new_value)
        return True
    if command in ("L", "++", "inc5"):
        new_value = apply_value(selected_key, values[selected_key] + 5)
        session["status"] = selected_key + " -> " + str(new_value)
        return True
    if command in ("1", "2", "3", "4"):
        session["focus_index"] = set_focus(int(command) - 1)
        session["status"] = "Preview focus -> " + FOCUS_NAMES[session["focus_index"]]
        return True
    if command in ("a", "auto"):
        session["auto_cycle"] = not session["auto_cycle"]
        session["next_cycle_at"] = now + AUTO_CYCLE_SECS
        session["status"] = "Auto-cycle " + (
            "enabled" if session["auto_cycle"] else "disabled"
        )
        return True
    if command in ("c", "sample"):
        session["sample_index"] = (session["sample_index"] + 1) % len(SAMPLE_CASES)
        session["sample"] = dict(SAMPLE_CASES[session["sample_index"]])
        configure_form(session["sample"])
        session["focus_index"] = set_focus(session["focus_index"])
        session["status"] = "Loaded preset sample: " + session["sample"]["name"]
        return True
    if command in ("x", "random"):
        session["sample"] = build_random_case()
        configure_form(session["sample"])
        session["focus_index"] = set_focus(session["focus_index"])
        session["status"] = "Loaded random sample input values."
        return True
    if command in ("s", "save"):
        saved_path = fbu.save_compact_tuning()
        session["status"] = (
            "Saved tuning to " + saved_path if saved_path else "Save failed."
        )
        return True
    if command in ("r", "reload"):
        changed = reload_saved()
        if changed:
            session["status"] = "Reloaded saved tuning."
        elif os.path.exists(fbu.COMPACT_TUNE_FILE):
            session["status"] = "Saved file loaded with no changes."
        else:
            session["status"] = "No saved tuning file found yet."
        return True
    if command in ("d", "defaults", "reset"):
        reset_defaults()
        session["status"] = "Reset to compact defaults."
        return True
    if command in ("show", "status"):
        session["status"] = "Showing current tuner state."
        return True
    if command == "help":
        session["status"] = "Displayed help."
        print_line_help()
        return True

    parts = command.split()
    if len(parts) == 2 and parts[0] == "focus" and parts[1] in ("1", "2", "3", "4"):
        session["focus_index"] = set_focus(int(parts[1]) - 1)
        session["status"] = "Preview focus -> " + FOCUS_NAMES[session["focus_index"]]
        return True

    if len(parts) == 3 and parts[0] == "set":
        target_key = parts[1].strip()
        if target_key not in keys:
            session["status"] = "Unknown key: " + target_key
            return True
        try:
            target_value = int(parts[2])
        except Exception:
            session["status"] = "Invalid value: " + parts[2]
            return True
        new_value = apply_value(target_key, target_value)
        session["selected_index"] = keys.index(target_key)
        session["status"] = target_key + " -> " + str(new_value)
        return True

    session["status"] = "Unknown command: " + command
    return True


def run_raw_mode(previous_form_state, keys):
    session = init_session()
    last_refresh = 0.0
    last_render = 0.0

    try:
        with RawTerminal(sys.stdin):
            while True:
                last_refresh, keep_running = tick_preview(session, last_refresh)
                if not keep_running:
                    break

                now = time.monotonic()
                if now - last_render >= 0.12:
                    render_screen(
                        current_tuning(),
                        session["selected_index"],
                        session["focus_index"],
                        session["auto_cycle"],
                        session["sample"]["name"],
                        session["status"],
                    )
                    last_render = now

                key = read_key(timeout=0.03)
                if key is None:
                    continue

                raw_commands = {
                    "DOWN": "j",
                    "UP": "k",
                    "LEFT": "h",
                    "RIGHT": "l",
                }
                if not apply_command(raw_commands.get(key, key), session, keys):
                    break

                render_screen(
                    current_tuning(),
                    session["selected_index"],
                    session["focus_index"],
                    session["auto_cycle"],
                    session["sample"]["name"],
                    session["status"],
                )
                last_render = time.monotonic()
    finally:
        if sys.stdout.isatty():
            sys.stdout.write("\x1b[2J\x1b[H")
            sys.stdout.flush()
        restore_form_state(previous_form_state)

    print("Live tuner closed.")
    return 0


def run_line_mode(previous_form_state, keys):
    session = init_session()
    last_refresh = 0.0
    pending = ""

    print_line_help()
    print("Using command mode. Type a command and press Enter.")
    print_line_status(session, keys)

    try:
        while True:
            last_refresh, keep_running = tick_preview(session, last_refresh)
            if not keep_running:
                break

            ready, _, _ = select.select([sys.stdin], [], [], 0.03)
            if not ready:
                continue

            chunk = os.read(sys.stdin.fileno(), 1024)
            if not chunk:
                session["status"] = "Input stream closed."
                break

            pending += chunk.decode("utf-8", errors="ignore")
            pending = pending.replace("\r\n", "\n").replace("\r", "\n")

            while "\n" in pending:
                line, pending = pending.split("\n", 1)
                if not apply_command(line, session, keys):
                    print_line_status(session, keys)
                    return 0
                print_line_status(session, keys)
    finally:
        restore_form_state(previous_form_state)

    print("Live tuner closed.")
    return 0


def main():
    
    previous_form_state = capture_form_state()
    st7565.init(9, 11, 10, 13, 12)
    keys = list(fbu.COMPACT_TUNE_KEYS)
    force_line_mode = "--line" in sys.argv

    if force_line_mode or not sys.stdin.isatty():
        return run_line_mode(previous_form_state, keys)

    try:
        return run_raw_mode(previous_form_state, keys)
    except Exception as exc:
        print("Raw key mode failed, switching to command mode:", exc)
        return run_line_mode(previous_form_state, keys)


if __name__ == "__main__":
    raise SystemExit(main())
