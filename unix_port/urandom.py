try:
    import random as _random
except Exception:
    _random = None


def getrandbits(bits):
    if _random is None:
        return 0
    return _random.getrandbits(int(bits))


def randint(a, b):
    if _random is None:
        return int(a)
    return _random.randint(int(a), int(b))
