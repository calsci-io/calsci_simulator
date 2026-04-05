from __future__ import annotations

WAKEUP_ANY_HIGH = 1
WAKEUP_ALL_LOW = 2


def wake_on_ext0(pin=None, level=None):
    _ = (pin, level)


def gpio_deep_sleep_hold(enabled):
    _ = enabled


def raw_temperature():
    return 28.0


class Partition:
    TYPE_APP = 0
    RUNNING = 1

    _labels = ("ota_0", "ota_1", "ota_2")
    _running = "ota_0"

    def __init__(self, target):
        if target == Partition.RUNNING:
            self.label = Partition._running
        elif isinstance(target, str) and target in Partition._labels:
            self.label = target
        else:
            raise ValueError("Unknown partition target: %r" % (target,))

    @classmethod
    def find(cls, part_type):
        if part_type != cls.TYPE_APP:
            return []
        return [cls(label) for label in cls._labels]

    def info(self):
        return (b"app", self.label.encode(), 0x20000, 0x0, 0x0)

    def set_boot(self):
        Partition._running = self.label

    def __repr__(self):
        return "Partition(%s)" % self.label
