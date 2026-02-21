from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

from compat import install_compat

SIM_DIR = Path(__file__).resolve().parent
ROOT_DIR = SIM_DIR.parent
CALSCI_DIR = ROOT_DIR / "calsci_latest_itr"
LIB_DIR = CALSCI_DIR / "lib"

if not CALSCI_DIR.exists():
    raise RuntimeError("calsci_latest_itr directory not found next to simulator")

# Path order is important: simulator shims first, then firmware code + firmware lib.
ordered_paths = [str(SIM_DIR), str(CALSCI_DIR), str(LIB_DIR)]
for p in ordered_paths:
    if p in sys.path:
        sys.path.remove(p)
sys.path[:0] = ordered_paths

install_compat(calsci_dir=CALSCI_DIR, simulator_dir=SIM_DIR)
os.chdir(CALSCI_DIR)

# Bring up the display window before app boot.
import st7565

st7565.init(9, 11, 10, 13, 12)

runpy.run_path(str(CALSCI_DIR / "main.py"), run_name="__main__")
