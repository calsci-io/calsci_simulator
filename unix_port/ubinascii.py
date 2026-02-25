try:
    import binascii as _binascii
except Exception:
    _binascii = None


def hexlify(data):
    if _binascii is not None:
        return _binascii.hexlify(data)

    alphabet = b"0123456789abcdef"
    out = bytearray(len(data) * 2)
    j = 0
    for b in data:
        out[j] = alphabet[(b >> 4) & 0x0F]
        out[j + 1] = alphabet[b & 0x0F]
        j += 2
    return bytes(out)


def unhexlify(data):
    if _binascii is not None:
        return _binascii.unhexlify(data)

    if isinstance(data, str):
        data = data.encode()
    return bytes.fromhex(data.decode())


def b2a_base64(data):
    if _binascii is None:
        raise ValueError("base64 unavailable")
    return _binascii.b2a_base64(data)


def a2b_base64(data):
    if _binascii is None:
        raise ValueError("base64 unavailable")
    return _binascii.a2b_base64(data)
