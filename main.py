from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

from compat import install_compat
import sim_ui


def _external_calsci_dir() -> Path | None:
    override = os.environ.get("CALSCI_APP_DIR")
    if not override:
        return None
    return Path(override).expanduser().resolve()


def _resolve_simulator_dir() -> Path:
    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir:
        return Path(bundle_dir).resolve()
    return Path(__file__).resolve().parent


def _looks_like_calsci_dir(candidate: Path) -> bool:
    return (
        candidate.is_dir()
        and (candidate / "main.py").is_file()
        and (candidate / "apps").is_dir()
        and (candidate / "lib").is_dir()
    )


def _resolve_calsci_dir(simulator_dir: Path) -> Path:
    candidates = []

    override_dir = _external_calsci_dir()
    if override_dir is not None:
        candidates.append(override_dir)

    # In PyInstaller onedir builds, let an app tree placed next to the executable
    # override the bundled copy so branch swaps can be tested without rebuilding.
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent / "calsci_latest_itr")

    candidates.extend(
        (
            simulator_dir / "calsci_latest_itr",
            simulator_dir.parent / "calsci_latest_itr",
        )
    )

    for candidate in candidates:
        if _looks_like_calsci_dir(candidate):
            return candidate

    raise RuntimeError(
        "calsci_latest_itr directory not found. Run "
        "'git submodule update --init --recursive --remote' from the simulator repo "
        "or set CALSCI_APP_DIR to override the app tree."
    )


SIM_DIR = _resolve_simulator_dir()
CALSCI_DIR = _resolve_calsci_dir(SIM_DIR)
LIB_DIR = CALSCI_DIR / "lib"

# Path order is important: simulator shims first, then firmware code + firmware lib.
ordered_paths = [str(SIM_DIR), str(CALSCI_DIR), str(LIB_DIR)]
for p in ordered_paths:
    if p in sys.path:
        sys.path.remove(p)
sys.path[:0] = ordered_paths

install_compat(calsci_dir=CALSCI_DIR, simulator_dir=SIM_DIR)


def _restart_simulator():
    sim_ui.shutdown_ui()
    os.chdir(SIM_DIR)

    if getattr(sys, "frozen", False):
        os.execv(sys.executable, [sys.executable, *sys.argv[1:]])

    os.execv(sys.executable, [sys.executable, str(SIM_DIR / "main.py"), *sys.argv[1:]])


def _run_simulator_app():
    os.chdir(CALSCI_DIR)

    # Bring up the display window before app boot.
    import st7565

    st7565.init(9, 11, 10, 13, 12)
    runpy.run_path(str(CALSCI_DIR / "main.py"), run_name="__main__")


try:
    _run_simulator_app()
except SystemExit as exc:
    if exc.code == sim_ui.RELOAD_EXIT_CODE:
        _restart_simulator()
    raise
