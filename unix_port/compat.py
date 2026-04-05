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


def _to_str_path(path):
    if isinstance(path, str):
        return path
    if isinstance(path, bytes):
        try:
            return path.decode()
        except Exception:
            return None
    return None


def _abspath(path):
    os_path = getattr(os, "path", None)
    if os_path is not None and hasattr(os_path, "abspath"):
        return os_path.abspath(path)
    if path.startswith("/"):
        return path
    cwd = os.getcwd()
    if cwd.endswith("/"):
        return cwd + path
    return cwd + "/" + path


def _build_mapper(calsci_dir, simulator_dir):
    calsci_dir = _abspath(calsci_dir)
    simulator_dir = _abspath(simulator_dir)

    def map_path(path):
        text = _to_str_path(path)
        if text is None:
            return path

        if not text.startswith("/"):
            return path

        rel = text[1:]
        if not rel:
            return path

        if "/" in rel:
            head, tail = rel.split("/", 1)
        else:
            head, tail = rel, ""

        mapped_head = _PREFIX_MAP.get(head)
        if mapped_head is None:
            return path

        if head == "certs":
            mapped = simulator_dir + "/certs"
        else:
            mapped = calsci_dir + "/" + mapped_head

        if tail:
            mapped = mapped + "/" + tail

        return mapped

    return map_path


def _wrap_one_arg(func, mapper):
    def wrapped(path, *args, **kwargs):
        return func(mapper(path), *args, **kwargs)

    return wrapped


def _wrap_two_arg(func, mapper):
    def wrapped(path_a, path_b, *args, **kwargs):
        return func(mapper(path_a), mapper(path_b), *args, **kwargs)

    return wrapped


def install_compat(calsci_dir, simulator_dir):
    global _PATCHED

    if _PATCHED:
        return

    map_path = _build_mapper(calsci_dir=calsci_dir, simulator_dir=simulator_dir)

    original_open = builtins.open

    def open_wrapper(file, *args, **kwargs):
        return original_open(map_path(file), *args, **kwargs)

    builtins.open = open_wrapper

    for name in ("listdir", "mkdir", "makedirs", "remove", "unlink", "rmdir", "stat", "scandir"):
        if hasattr(os, name):
            try:
                setattr(os, name, _wrap_one_arg(getattr(os, name), map_path))
            except Exception:
                # Some unix-port modules expose read-only attributes.
                pass

    for name in ("rename", "replace"):
        if hasattr(os, name):
            try:
                setattr(os, name, _wrap_two_arg(getattr(os, name), map_path))
            except Exception:
                pass

    os_path = getattr(os, "path", None)
    if os_path is not None:
        for name in ("exists", "isdir", "isfile", "abspath", "realpath", "getsize"):
            if hasattr(os_path, name):
                try:
                    setattr(os_path, name, _wrap_one_arg(getattr(os_path, name), map_path))
                except Exception:
                    pass

    if not hasattr(builtins, "const"):
        builtins.const = lambda value: value

    if not hasattr(gc, "mem_free"):
        gc.mem_free = lambda: 0
    if not hasattr(gc, "mem_alloc"):
        gc.mem_alloc = lambda: 0

    if not hasattr(time, "sleep_ms"):
        time.sleep_ms = lambda ms: time.sleep(float(ms) / 1000.0)
    if not hasattr(time, "sleep_us"):
        time.sleep_us = lambda us: time.sleep(float(us) / 1000000.0)
    if not hasattr(time, "ticks_ms"):
        time.ticks_ms = lambda: int(time.time() * 1000)
    if not hasattr(time, "ticks_us"):
        time.ticks_us = lambda: int(time.time() * 1000000)
    if not hasattr(time, "ticks_diff"):
        time.ticks_diff = lambda new, old: int(new) - int(old)
    if not hasattr(time, "ticks_add"):
        time.ticks_add = lambda base, delta: int(base) + int(delta)

    _PATCHED = True
