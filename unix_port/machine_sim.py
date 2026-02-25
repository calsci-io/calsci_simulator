import random


mem8 = bytearray(1024)
mem16 = bytearray(1024)
mem32 = bytearray(1024)

_irq_state = 0
_cpu_freq = 240000000

# Default keypad matrix used by calsci_latest_itr/data_modules/object_handler.py
_MATRIX_ROWS = (14, 21, 47, 48, 38, 39, 40, 41, 42, 1)
_MATRIX_COLS = (8, 18, 17, 15, 7)


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
    _pressed_queue = []
    _active_press = None

    def __init__(self, id, mode=-1, pull=-1, value=0, drive=0, alt=-1, hold=False):
        self.id = int(id)
        state = Pin._states.get(self.id)

        if state is None:
            state = {
                "mode": Pin.IN,
                "pull": -1,
                "value": 1,
                "drive": 0,
                "alt": -1,
                "hold": False,
            }
            Pin._states[self.id] = state

        if mode != -1:
            state["mode"] = mode
        if pull != -1:
            state["pull"] = pull

        state["drive"] = drive
        state["alt"] = alt
        state["hold"] = bool(hold)

        if state["mode"] in (Pin.OUT, Pin.OPEN_DRAIN):
            state["value"] = 1 if value else 0

    @classmethod
    def configure_matrix(cls, rows=None, cols=None):
        global _MATRIX_ROWS, _MATRIX_COLS
        if rows is not None:
            _MATRIX_ROWS = tuple(rows)
        if cols is not None:
            _MATRIX_COLS = tuple(cols)

    @classmethod
    def queue_key(cls, col, row):
        cls._pressed_queue.append((int(col), int(row)))

    @classmethod
    def clear_keys(cls):
        cls._pressed_queue = []
        cls._active_press = None

    @classmethod
    def _maybe_read_matrix_col(cls, pin_id):
        if pin_id not in _MATRIX_COLS:
            return None

        if cls._active_press is None and cls._pressed_queue:
            cls._active_press = cls._pressed_queue.pop(0)

        active = cls._active_press
        if active is None:
            return 1

        target_col, target_row = active
        if target_col < 0 or target_row < 0:
            cls._active_press = None
            return 1
        if target_col >= len(_MATRIX_COLS) or target_row >= len(_MATRIX_ROWS):
            cls._active_press = None
            return 1

        active_row_pin = _MATRIX_ROWS[target_row]
        row_state = cls._states.get(active_row_pin, {"value": 1})

        if row_state.get("value", 1) != 0:
            return 1

        if pin_id == _MATRIX_COLS[target_col]:
            cls._active_press = None
            return 0

        return 1

    def init(self, mode=-1, pull=-1, value=0, drive=0, alt=-1, hold=False):
        self.__init__(self.id, mode=mode, pull=pull, value=value, drive=drive, alt=alt, hold=hold)

    def value(self, *args):
        state = Pin._states[self.id]

        if not args:
            if state["mode"] == Pin.IN:
                matrix_value = Pin._maybe_read_matrix_col(self.id)
                if matrix_value is not None:
                    return matrix_value
            return state["value"]

        state["value"] = 1 if args[0] else 0
        return state["value"]

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)

    def low(self):
        self.value(0)

    def high(self):
        self.value(1)

    def irq(self, trigger=0, priority=1, wake=None, hard=False, handler=None):
        _ = (trigger, priority, wake, hard, handler)

    def mode(self, mode=None):
        state = Pin._states[self.id]
        if mode is None:
            return state["mode"]
        state["mode"] = mode
        return state["mode"]

    def pull(self, pull=None):
        state = Pin._states[self.id]
        if pull is None:
            return state["pull"]
        state["pull"] = pull
        return state["pull"]

    def drive(self, drive=None):
        state = Pin._states[self.id]
        if drive is None:
            return state["drive"]
        state["drive"] = drive
        return state["drive"]

    def toggle(self):
        self.value(0 if self.value() else 1)


class Timer:
    ONE_SHOT = 0
    PERIODIC = 1

    def __init__(self, id=-1):
        self.id = id
        self._callback = None
        self._mode = Timer.ONE_SHOT
        self._period = 0

    def init(self, mode=ONE_SHOT, period=-1, callback=None):
        self._mode = mode
        self._period = int(period)
        self._callback = callback

    def deinit(self):
        self._callback = None


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
        self._value = 2048

    def atten(self, value=None):
        if value is None:
            return self._atten
        self._atten = value

    def width(self, value=None):
        if value is None:
            return self._width
        self._width = value

    def read(self):
        return int(self._value)

    def read_u16(self):
        return int((self._value & 0x0FFF) * 16)


class PWM:
    def __init__(self, pin, freq=1000, duty=None, duty_u16=None, duty_ns=None, invert=False):
        self.pin = pin
        self._freq = int(freq)
        self._invert = bool(invert)
        self._duty = 0
        self._duty_u16 = 0
        self._duty_ns = 0

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


class SoftSPI:
    LSB = 0
    MSB = 1

    def __init__(self, baudrate=500000, polarity=0, phase=0, bits=8, firstbit=MSB, sck=None, mosi=None, miso=None):
        self.baudrate = baudrate
        self.polarity = polarity
        self.phase = phase
        self.bits = bits
        self.firstbit = firstbit
        self.sck = sck
        self.mosi = mosi
        self.miso = miso

    def init(self, baudrate=500000, polarity=0, phase=0, bits=8, firstbit=MSB):
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

    def write(self, data):
        _ = data

    def write_readinto(self, src, dst):
        count = min(len(src), len(dst))
        for i in range(count):
            dst[i] = src[i]


def reset():
    print("[unix-port] machine.reset() requested (ignored)")


def soft_reset():
    print("[unix-port] machine.soft_reset() requested (ignored)")


def reset_cause():
    return 0


def bootloader(value=None):
    _ = value


def disable_irq():
    global _irq_state
    previous = _irq_state
    _irq_state = 1
    return previous


def enable_irq(state):
    global _irq_state
    _irq_state = int(state)


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
    _ = time_ms


def deepsleep(time_ms=None):
    _ = time_ms
    print("[unix-port] machine.deepsleep() requested (ignored)")


def wake_reason():
    return 0


def unique_id():
    return bytes((0xCA, 0x1A, 0x5C, 0x10, 0x00, 0x29))


def time_pulse_us(pin, pulse_level, timeout_us=1000000):
    _ = (pin, pulse_level, timeout_us)
    return random.randint(100, 50000)


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


# Helper functions for tests / unix port usage.
def queue_key(col, row):
    Pin.queue_key(col=col, row=row)


def clear_keys():
    Pin.clear_keys()
