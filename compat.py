from __future__ import annotations

import builtins
import gc
import os
import time


_PREFIX_MAP = {
    "db": "db",
    "database": "db",
    "apps": "apps",
    "lib": "lib",
    "certs": "certs",
}


_PATCHED = False


def _path_to_str(path):
    try:
        return os.fspath(path)
    except TypeError:
        return path


def _build_mapper(calsci_dir, simulator_dir=None):
    calsci_dir = os.path.abspath(str(calsci_dir))
    simulator_dir = os.path.abspath(str(simulator_dir)) if simulator_dir else None

    def map_path(path):
        p = _path_to_str(path)
        if not isinstance(p, str):
            return path

        if p.startswith("/"):
            rel = p.lstrip("/")
            if not rel:
                return p

            head, sep, tail = rel.partition("/")
            mapped_head = _PREFIX_MAP.get(head)
            if mapped_head is None:
                return p

            if head == "certs" and simulator_dir:
                mapped = os.path.join(simulator_dir, "certs")
            else:
                mapped = os.path.join(calsci_dir, mapped_head)
            if sep:
                mapped = os.path.join(mapped, tail)
            return mapped

        return p

    return map_path


def _wrap_one_arg(func, mapper):
    def wrapped(path, *args, **kwargs):
        return func(mapper(path), *args, **kwargs)

    return wrapped


def _wrap_two_arg(func, mapper):
    def wrapped(path1, path2, *args, **kwargs):
        return func(mapper(path1), mapper(path2), *args, **kwargs)

    return wrapped


def install_compat(calsci_dir, simulator_dir=None):
    global _PATCHED
    if _PATCHED:
        return

    map_path = _build_mapper(calsci_dir, simulator_dir=simulator_dir)

    original_open = builtins.open

    def open_wrapper(file, *args, **kwargs):
        return original_open(map_path(file), *args, **kwargs)

    builtins.open = open_wrapper

    # os module path-based wrappers
    for name in ("listdir", "mkdir", "makedirs", "remove", "unlink", "rmdir", "stat", "scandir"):
        if hasattr(os, name):
            setattr(os, name, _wrap_one_arg(getattr(os, name), map_path))

    for name in ("rename", "replace"):
        if hasattr(os, name):
            setattr(os, name, _wrap_two_arg(getattr(os, name), map_path))

    # os.path wrappers used by the runtime
    for name in ("exists", "isdir", "isfile", "abspath", "realpath", "getsize"):
        if hasattr(os.path, name):
            setattr(os.path, name, _wrap_one_arg(getattr(os.path, name), map_path))

    # MicroPython helpers expected by firmware code.
    if not hasattr(builtins, "const"):
        builtins.const = lambda value: value

    if not hasattr(gc, "mem_free"):
        gc.mem_free = lambda: 0
    if not hasattr(gc, "mem_alloc"):
        gc.mem_alloc = lambda: 0

    if not hasattr(time, "sleep_ms"):
        time.sleep_ms = lambda ms: time.sleep(float(ms) / 1000.0)
    if not hasattr(time, "sleep_us"):
        time.sleep_us = lambda us: time.sleep(float(us) / 1_000_000.0)
    if not hasattr(time, "ticks_ms"):
        time.ticks_ms = lambda: int(time.monotonic() * 1000)
    if not hasattr(time, "ticks_us"):
        time.ticks_us = lambda: int(time.monotonic() * 1_000_000)
    if not hasattr(time, "ticks_diff"):
        time.ticks_diff = lambda new, old: int(new) - int(old)

    _PATCHED = True
