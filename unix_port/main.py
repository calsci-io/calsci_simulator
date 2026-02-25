import os
import sys

from runtime_bootstrap import bootstrap


def _dirname(path):
    os_path = getattr(os, "path", None)
    if os_path is not None and hasattr(os_path, "dirname"):
        return os_path.dirname(path)
    idx = path.rfind("/")
    if idx < 0:
        return "."
    if idx == 0:
        return "/"
    return path[:idx]


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


def _exec_file(path):
    glb = {
        "__name__": "__main__",
        "__file__": path,
    }
    with open(path, "r") as f:
        code = f.read()
    exec(compile(code, path, "exec"), glb, glb)


def _isdir(path):
    os_path = getattr(os, "path", None)
    if os_path is not None and hasattr(os_path, "isdir"):
        return os_path.isdir(path)
    try:
        mode = os.stat(path)[0]
    except Exception:
        return False
    return bool(mode & 0x4000)


def _run_smoke(calsci_dir):
    os.chdir(calsci_dir)

    import st7565

    st7565.init(9, 11, 10, 13, 12)

    import data_modules.object_handler
    import process_modules.app_runner
    import apps.root.home

    print("unix-port smoke ok")


def _print_lvgl_runtime():
    try:
        import lvgl
    except Exception as exc:
        print("[unix-port] lvgl runtime: unavailable ({})".format(type(exc).__name__))
        return

    if hasattr(lvgl, "version_major"):
        try:
            ver = "{}.{}.{}".format(lvgl.version_major(), lvgl.version_minor(), lvgl.version_patch())
        except Exception:
            ver = "unknown"
        print("[unix-port] lvgl runtime: native ({})".format(ver))
        return

    print("[unix-port] lvgl runtime: stub")


def main():
    script_path = _abspath(__file__)
    unix_port_dir = _dirname(script_path)
    simulator_dir = _dirname(unix_port_dir)
    root_dir = _dirname(simulator_dir)
    calsci_dir = root_dir + "/calsci_latest_itr"

    if not _isdir(calsci_dir):
        raise OSError("calsci_latest_itr directory not found next to simulator")

    bootstrap(unix_port_dir=unix_port_dir, calsci_dir=calsci_dir, simulator_dir=simulator_dir)
    _print_lvgl_runtime()

    if "--smoke" in sys.argv:
        _run_smoke(calsci_dir=calsci_dir)
        return

    os.chdir(calsci_dir)

    import st7565

    st7565.init(9, 11, 10, 13, 12)

    if "--skip-boot" not in sys.argv:
        _exec_file(calsci_dir + "/boot.py")

    _exec_file(calsci_dir + "/main.py")


main()
