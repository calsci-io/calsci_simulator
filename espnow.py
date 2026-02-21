class ESPNow:
    def __init__(self):
        self._active = False

    def active(self, enabled=None):
        if enabled is None:
            return self._active
        self._active = bool(enabled)

    def add_peer(self, peer):
        _ = peer

    def send(self, peer, msg, sync=True):
        _ = (peer, msg, sync)
        return True

    def recv(self, timeout_ms=0):
        _ = timeout_ms
        return None, None

    def irecv(self):
        return None
