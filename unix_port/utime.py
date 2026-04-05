import time as _time


sleep = _time.sleep


def sleep_ms(ms):
    if hasattr(_time, "sleep_ms"):
        return _time.sleep_ms(ms)
    return _time.sleep(float(ms) / 1000.0)


def sleep_us(us):
    if hasattr(_time, "sleep_us"):
        return _time.sleep_us(us)
    return _time.sleep(float(us) / 1000000.0)


def ticks_ms():
    if hasattr(_time, "ticks_ms"):
        return _time.ticks_ms()
    return int(_time.time() * 1000)


def ticks_us():
    if hasattr(_time, "ticks_us"):
        return _time.ticks_us()
    return int(_time.time() * 1000000)


def ticks_diff(new, old):
    if hasattr(_time, "ticks_diff"):
        return _time.ticks_diff(new, old)
    return int(new) - int(old)


def ticks_add(base, delta):
    if hasattr(_time, "ticks_add"):
        return _time.ticks_add(base, delta)
    return int(base) + int(delta)


def time():
    return int(_time.time())


def localtime(secs=None):
    if secs is None:
        return _time.localtime()
    return _time.localtime(secs)


def mktime(t):
    return int(_time.mktime(t))
