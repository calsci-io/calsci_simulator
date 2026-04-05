# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


SPEC_DIR = Path(SPECPATH).resolve()
BACKGROUND_IMAGE = SPEC_DIR / "Untitled.jpeg"


def _resolve_calsci_dir():
    candidates = (
        (SPEC_DIR / "calsci_latest_itr").resolve(),
        (SPEC_DIR.parent / "calsci_latest_itr").resolve(),
    )
    for candidate in candidates:
        if (candidate / "main.py").is_file() and (candidate / "apps").is_dir():
            return candidate
    raise SystemExit("calsci_latest_itr directory not found in or next to simulator")


CALSCI_DIR = _resolve_calsci_dir()


def _collect_data_files(root_dir, dest_prefix):
    root_dir = Path(root_dir)
    collected = []
    for path in root_dir.rglob("*"):
        if not path.is_file():
            continue

        rel_path = path.relative_to(root_dir)
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in rel_path.parts):
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue

        dest_dir = Path(dest_prefix) / rel_path.parent
        collected.append((str(path), str(dest_dir)))
    return collected


datas = _collect_data_files(CALSCI_DIR, "calsci_latest_itr")
datas += _collect_data_files(SPEC_DIR / "certs", "certs")

if BACKGROUND_IMAGE.is_file():
    datas += [(str(BACKGROUND_IMAGE), ".")]


hiddenimports = [
    "dht",
    "esp32",
    "espnow",
    "lvgl",
    "machine",
    "network",
    "ntptime",
    "requests",
    "settings",
    "sim_ui",
    "st7565",
    "ubinascii",
    "ujson",
    "umqtt",
    "urandom",
    "urequests",
    "utime",
] + collect_submodules("settings") + collect_submodules("umqtt")


a = Analysis(
    ["main.py"],
    pathex=[str(SPEC_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="calsci_simulator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="calsci_simulator",
)
