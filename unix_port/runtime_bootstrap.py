import sys

from compat import install_compat


def _prepend_paths(paths):
    cleaned = []
    for path in paths:
        if path and path not in cleaned:
            cleaned.append(path)

    for path in cleaned:
        if path in sys.path:
            sys.path.remove(path)

    for i in range(len(cleaned) - 1, -1, -1):
        sys.path.insert(0, cleaned[i])


def _install_lvgl_fallback():
    try:
        __import__("lvgl")
    except Exception:
        import lvgl_stub

        sys.modules["lvgl"] = lvgl_stub


def bootstrap(unix_port_dir, calsci_dir, simulator_dir):
    lib_dir = calsci_dir + "/lib"
    _prepend_paths([unix_port_dir, calsci_dir, lib_dir])

    install_compat(calsci_dir=calsci_dir, simulator_dir=simulator_dir)
    _install_lvgl_fallback()

    import os_sim
    import machine_sim

    os_sim.configure(calsci_dir=calsci_dir, simulator_dir=simulator_dir)
    sys.modules["os"] = os_sim

    # Force CalSci imports to use the shim instead of unix port's built-in machine module.
    sys.modules["machine"] = machine_sim
