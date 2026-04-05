from __future__ import annotations

import time as _time

import sim_ui


_EVENT_POLL_SLICE_SECONDS = 0.01


def _sleep_with_events(seconds):
    seconds = float(seconds)
    if seconds <= 0:
        return None

    if not sim_ui.STATE.initialized:
        return _time.sleep(seconds)

    deadline = _time.monotonic() + seconds
    while True:
        sim_ui.poll_events()

        remaining = deadline - _time.monotonic()
        if remaining <= 0:
            break

        _time.sleep(min(_EVENT_POLL_SLICE_SECONDS, remaining))

    return None


def sleep(seconds):
    return _sleep_with_events(seconds)


def sleep_ms(ms):
    return _sleep_with_events(float(ms) / 1000.0)


def sleep_us(us):
    return _sleep_with_events(float(us) / 1_000_000.0)


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
