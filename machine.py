from __future__ import annotations

import random

import sim_ui

mem8 = []
mem16 = []
mem32 = []

_irq_state = 0
_cpu_freq = 240_000_000


def reset():
    print("[sim] machine.reset() requested (ignored)")


def soft_reset():
    print("[sim] machine.soft_reset() requested (ignored)")


def reset_cause():
    return 0


def bootloader(value=None):
    print("[sim] machine.bootloader()", value)


def disable_irq():
    global _irq_state
    prev = _irq_state
    _irq_state = 1
    return prev


def enable_irq(state):
    global _irq_state
    _irq_state = state


def freq(value=None):
    global _cpu_freq
    if value is None:
        return _cpu_freq
    _cpu_freq = int(value)
    return _cpu_freq


def idle():
    return None


def sleep():
    return None


def lightsleep(time_ms=None):
    print("[sim] machine.lightsleep()", time_ms)


def deepsleep(time_ms=None):
    print("[sim] machine.deepsleep()", time_ms)


def wake_reason():
    return 0


def unique_id():
    return bytes((0xCA, 0x1A, 0x5C, 0x10, 0x00, 0x29))


def time_pulse_us(pin, pulse_level, timeout_us=1000000):
    _ = (pin, pulse_level, timeout_us)
    return random.randint(100, 50_000)


def bitstream(pin, encoding, timing, data):
    _ = (pin, encoding, timing, data)


def rng():
    return random.getrandbits(30)


IDLE = 0
SLEEP = 1
DEEPSLEEP = 2

PWRON_RESET = 0
HARD_RESET = 1
WDT_RESET = 2
DEEPSLEEP_RESET = 3
SOFT_RESET = 4

WLAN_WAKE = 0
PIN_WAKE = 1
RTC_WAKE = 2


class Pin:
    IN = 1
    OUT = 3
    OPEN_DRAIN = 5
    ALT = 7
    ALT_OPEN_DRAIN = 9
    ANALOG = 2

    PULL_UP = 1
    PULL_DOWN = 2
    PULL_HOLD = 4

    DRIVE_0 = 0
    DRIVE_1 = 1
    DRIVE_2 = 2

    IRQ_FALLING = 0x02
    IRQ_RISING = 0x01
    IRQ_LOW_LEVEL = 0x04
    IRQ_HIGH_LEVEL = 0x08

    _states = {}

    def __init__(self, id, mode=-1, pull=-1, *, value=0, drive=0, alt=-1, hold=False):
        sim_ui.ensure_ui()

        self.id = int(id)
        st = self._states.setdefault(
            self.id,
            {
                "mode": Pin.IN,
                "pull": -1,
                "value": 1,
                "drive": 0,
                "alt": -1,
                "hold": False,
            },
        )

        if mode != -1:
            st["mode"] = mode
        if pull != -1:
            st["pull"] = pull

        st["drive"] = drive
        st["alt"] = alt
        st["hold"] = hold

        if st["mode"] in (Pin.OUT, Pin.OPEN_DRAIN):
            st["value"] = 1 if value else 0
            if self.id in sim_ui.ROW_PINS:
                sim_ui.set_row_level(self.id, st["value"])

    def init(self, mode=-1, pull=-1, *, value=0, drive=0, alt=-1, hold=False):
        self.__init__(self.id, mode=mode, pull=pull, value=value, drive=drive, alt=alt, hold=hold)

    def value(self, *args):
        st = self._states[self.id]

        if not args:
            sim_ui.poll_events()
            if st["mode"] == Pin.IN and self.id in sim_ui.COL_PINS:
                return sim_ui.read_col_pin(self.id)
            return st["value"]

        val = 1 if args[0] else 0
        st["value"] = val
        if self.id in sim_ui.ROW_PINS:
            sim_ui.set_row_level(self.id, val)
        return val

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)

    def low(self):
        self.value(0)

    def high(self):
        self.value(1)

    def irq(self, trigger, *, priority=1, wake=None, hard=False, handler=None):
        _ = (trigger, priority, wake, hard, handler)

    def mode(self, mode=None):
        st = self._states[self.id]
        if mode is None:
            return st["mode"]
        st["mode"] = mode
        return st["mode"]

    def pull(self, pull=None):
        st = self._states[self.id]
        if pull is None:
            return st["pull"]
        st["pull"] = pull
        return st["pull"]

    def drive(self, drive=None):
        st = self._states[self.id]
        if drive is None:
            return st["drive"]
        st["drive"] = drive
        return st["drive"]

    def toggle(self):
        self.value(0 if self.value() else 1)


class Timer:
    ONE_SHOT = 0
    PERIODIC = 1

    def __init__(self, id=-1):
        self.id = id
        self._callback = None
        self._period = 0
        self._mode = Timer.PERIODIC

    def init(self, *, mode=PERIODIC, period=-1, callback=None):
        self._mode = mode
        self._period = period
        self._callback = callback

    def deinit(self):
        self._callback = None


class SoftSPI:
    LSB = 0
    MSB = 1

    def __init__(self, baudrate=500000, *, polarity=0, phase=0, bits=8, firstbit=MSB, sck=None, mosi=None, miso=None):
        self.baudrate = baudrate
        self.polarity = polarity
        self.phase = phase
        self.bits = bits
        self.firstbit = firstbit
        self.sck = sck
        self.mosi = mosi
        self.miso = miso

    def init(self, baudrate=500000, *, polarity=0, phase=0, bits=8, firstbit=MSB):
        self.baudrate = baudrate
        self.polarity = polarity
        self.phase = phase
        self.bits = bits
        self.firstbit = firstbit

    def deinit(self):
        return None

    def read(self, nbytes, write=0x00):
        _ = write
        return bytes([0] * int(nbytes))

    def readinto(self, buf, write=0x00):
        _ = write
        for i in range(len(buf)):
            buf[i] = 0

    def write(self, buf):
        _ = buf

    def write_readinto(self, write_buf, read_buf):
        _ = write_buf
        for i in range(len(read_buf)):
            read_buf[i] = 0


class ADC:
    ATTN_0DB = 0
    ATTN_2_5DB = 1
    ATTN_6DB = 2
    ATTN_11DB = 3
    WIDTH_9BIT = 9
    WIDTH_10BIT = 10
    WIDTH_11BIT = 11
    WIDTH_12BIT = 12

    def __init__(self, pin):
        self.pin = pin
        self._atten = ADC.ATTN_11DB
        self._width = ADC.WIDTH_12BIT
        self._value = 36000

    def atten(self, value=None):
        if value is None:
            return self._atten
        self._atten = value

    def width(self, value=None):
        if value is None:
            return self._width
        self._width = value

    def read_u16(self):
        return self._value

    def read(self):
        return self._value >> 4


class PWM:
    def __init__(self, pin, *, freq=1000, duty=None, duty_u16=None, duty_ns=None, invert=False):
        self.pin = pin
        self._freq = int(freq)
        self._invert = bool(invert)
        self._duty = 0
        self._duty_u16 = 0
        self._duty_ns = 0

        # Keep constructor behavior close to ESP32 MicroPython:
        # explicit duty_u16 wins, then duty, then duty_ns.
        if duty_u16 is not None:
            self.duty_u16(duty_u16)
        elif duty is not None:
            self.duty(duty)
        elif duty_ns is not None:
            self.duty_ns(duty_ns)

    def freq(self, value=None):
        if value is None:
            return self._freq
        self._freq = int(value)
        return self._freq

    def duty(self, value=None):
        # Legacy ESP32 API: 10-bit range [0, 1023]
        if value is None:
            return self._duty
        level = max(0, min(1023, int(value)))
        self._duty = level
        self._duty_u16 = level << 6
        return self._duty

    def duty_u16(self, value=None):
        if value is None:
            return self._duty_u16
        level = max(0, min(65535, int(value)))
        self._duty_u16 = level
        self._duty = level >> 6
        return self._duty_u16

    def duty_ns(self, value=None):
        if value is None:
            return self._duty_ns
        self._duty_ns = max(0, int(value))
        return self._duty_ns

    def invert(self, value=None):
        if value is None:
            return self._invert
        self._invert = bool(value)
        return self._invert

    def deinit(self):
        return None
