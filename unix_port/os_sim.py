import os as _os


_PREFIX_MAP = {
    "db": "db",
    "database": "db",
    "apps": "apps",
    "lib": "lib",
    "certs": "certs",
}

_CALSci_DIR = ""
_SIM_DIR = ""


def _to_text(path):
    if isinstance(path, str):
        return path
    if isinstance(path, bytes):
        try:
            return path.decode()
        except Exception:
            return None
    return None


def _dirname(path):
    idx = path.rfind("/")
    if idx < 0:
        return ""
    if idx == 0:
        return "/"
    return path[:idx]


def _join(base, name):
    if not base:
        return name
    if base.endswith("/"):
        return base + name
    return base + "/" + name


def _abspath(path):
    if path.startswith("/"):
        return path
    cwd = _os.getcwd()
    return _join(cwd, path)


def _map_path(path):
    text = _to_text(path)
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
        mapped = _join(_SIM_DIR, "certs")
    else:
        mapped = _join(_CALSci_DIR, mapped_head)

    if tail:
        mapped = _join(mapped, tail)

    return mapped


def _is_dir_mode(mode):
    return bool(mode & 0x4000)


def _is_file_mode(mode):
    return bool(mode & 0x8000)


def configure(calsci_dir, simulator_dir):
    global _CALSci_DIR, _SIM_DIR
    _CALSci_DIR = calsci_dir
    _SIM_DIR = simulator_dir


class _Path:
    @staticmethod
    def dirname(path):
        text = _to_text(path)
        if text is None:
            return ""
        return _dirname(text)

    @staticmethod
    def join(*parts):
        out = ""
        for part in parts:
            text = _to_text(part)
            if text is None or text == "":
                continue
            if text.startswith("/"):
                out = text
            else:
                out = _join(out, text)
        return out

    @staticmethod
    def exists(path):
        try:
            _os.stat(_map_path(path))
            return True
        except Exception:
            return False

    @staticmethod
    def isdir(path):
        try:
            mode = _os.stat(_map_path(path))[0]
            return _is_dir_mode(mode)
        except Exception:
            return False

    @staticmethod
    def isfile(path):
        try:
            mode = _os.stat(_map_path(path))[0]
            return _is_file_mode(mode)
        except Exception:
            return False

    @staticmethod
    def abspath(path):
        text = _to_text(path)
        if text is None:
            return path
        return _abspath(text)

    @staticmethod
    def realpath(path):
        return _Path.abspath(path)

    @staticmethod
    def getsize(path):
        return _os.stat(_map_path(path))[6]


path = _Path()
sep = "/"


def getcwd():
    return _os.getcwd()


def chdir(path):
    return _os.chdir(_map_path(path))


def listdir(path="."):
    return _os.listdir(_map_path(path))


def ilistdir(path="."):
    return _os.ilistdir(_map_path(path))


def mkdir(path):
    return _os.mkdir(_map_path(path))


def makedirs(path):
    mapped = _map_path(path)
    text = _to_text(mapped)
    if text is None:
        raise OSError("invalid path")

    current = ""
    if text.startswith("/"):
        current = "/"
        parts = [p for p in text.split("/") if p]
    else:
        parts = [p for p in text.split("/") if p]

    for part in parts:
        current = _join(current, part)
        try:
            _os.mkdir(current)
        except Exception:
            if not path_exists(current):
                raise


def remove(path):
    return _os.remove(_map_path(path))


def unlink(path):
    return _os.unlink(_map_path(path))


def rmdir(path):
    return _os.rmdir(_map_path(path))


def stat(path):
    return _os.stat(_map_path(path))


def statvfs(path):
    return _os.statvfs(_map_path(path))


def rename(src, dst):
    return _os.rename(_map_path(src), _map_path(dst))


def replace(src, dst):
    # unix MicroPython may not expose replace; fallback to rename.
    return _os.rename(_map_path(src), _map_path(dst))


def getenv(name):
    if hasattr(_os, "getenv"):
        return _os.getenv(name)
    return None


def putenv(name, value):
    if hasattr(_os, "putenv"):
        return _os.putenv(name, value)
    return None


def unsetenv(name):
    if hasattr(_os, "unsetenv"):
        return _os.unsetenv(name)
    return None


def urandom(n):
    if hasattr(_os, "urandom"):
        return _os.urandom(n)
    return bytes([0] * int(n))


def mount(*args, **kwargs):
    return _os.mount(*args, **kwargs)


def umount(*args, **kwargs):
    return _os.umount(*args, **kwargs)


def system(cmd):
    if hasattr(_os, "system"):
        return _os.system(cmd)
    return 0


def errno():
    if hasattr(_os, "errno"):
        return _os.errno()
    return 0


def path_exists(path):
    try:
        _os.stat(path)
        return True
    except Exception:
        return False


def __getattr__(name):
    return getattr(_os, name)
