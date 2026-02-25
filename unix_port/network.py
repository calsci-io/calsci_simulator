STA_IF = 0
AP_IF = 1

AUTH_OPEN = 0
AUTH_WPA_PSK = 2
AUTH_WPA2_PSK = 3
AUTH_WPA_WPA2_PSK = 4


class WLAN:
    _instances = {}

    def __new__(cls, interface):
        if interface in cls._instances:
            return cls._instances[interface]
        inst = object.__new__(cls)
        cls._instances[interface] = inst
        return inst

    def __init__(self, interface):
        if getattr(self, "_ready", False):
            return

        self.interface = interface
        self._active = False
        self._connected = False
        self._ssid = None
        self._password = None
        self._cfg = {
            "hostname": "CalSci-Unix",
            "ssid": "CalSci-Unix-AP",
            "mac": bytes((0xCA, 0x1A, 0x5C, 0x10, 0x00, 0x29)),
        }
        self._ifconfig = ("192.168.4.10", "255.255.255.0", "192.168.4.1", "8.8.8.8")
        self._ready = True

    def active(self, is_active=None):
        if is_active is None:
            return self._active
        self._active = bool(is_active)
        if not self._active:
            self._connected = False
        return self._active

    def config(self, *args, **kwargs):
        if args:
            key = args[0]
            return self._cfg.get(key)
        if kwargs:
            self._cfg.update(kwargs)
        return self._cfg

    def scan(self):
        return [
            (b"CalSciLab", b"\x00\x11\x22\x33\x44\x55", 1, -40, AUTH_WPA2_PSK, 0),
            (b"HomeWiFi", b"\x66\x77\x88\x99\xaa\xbb", 6, -55, AUTH_WPA2_PSK, 0),
            (b"Guest", b"\xcc\xdd\xee\xff\x00\x01", 11, -70, AUTH_OPEN, 0),
        ]

    def connect(self, ssid, password=None):
        if not self._active:
            return
        self._ssid = ssid
        self._password = password
        self._connected = True

    def disconnect(self):
        self._connected = False
        self._ssid = None

    def isconnected(self):
        return bool(self._active and self._connected)

    def ifconfig(self, config=None):
        if config is None:
            return self._ifconfig
        self._ifconfig = tuple(config)
        return self._ifconfig

    def status(self):
        return 3 if self.isconnected() else -1


def hostname(value=None):
    sta = WLAN(STA_IF)
    if value is None:
        return sta.config("hostname")
    sta.config(hostname=value)
    return value
