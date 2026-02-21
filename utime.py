from __future__ import annotations

import time as _time


def sleep(seconds):
    return _time.sleep(seconds)


def sleep_ms(ms):
    return _time.sleep(float(ms) / 1000.0)


def sleep_us(us):
    return _time.sleep(float(us) / 1_000_000.0)


def ticks_ms():
    return int(_time.monotonic() * 1000)


def ticks_us():
    return int(_time.monotonic() * 1_000_000)


def ticks_diff(new, old):
    return int(new) - int(old)


def time():
    return int(_time.time())


def localtime(secs=None):
    if secs is None:
        return _time.localtime()
    return _time.localtime(secs)


def mktime(t):
    return int(_time.mktime(t))
