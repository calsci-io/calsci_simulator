import random
mem8 = []
mem16 = []
mem32 = []

irq = None
frequency = random.randint(80, 240)


# TODO: needs to implemented
def reset():
    print("Hard reset was triggered")

def soft_reset():
    print("Soft reset was triggered")

def reset_cause():
    print("Reset cause was triggered")

def bootloader(value):
    print("bootloader triggered:", value)


def disable_irq():
    value = irq
    irq=None
    return value

def enable_irq(state):
    irq=state


def freq(freq):
    if freq:
        frequency = freq
    else:
        return frequency

def idle():
    print("idle state was triggered")


def sleep():
    print("deprecated sleep state was triggered")

def lightsleep(time_ms):
    print("lightsleep state was triggered", time_ms)


def deepsleep(time_ms):
    print("deepsleep state was triggered", time_ms)

def wake_reason():
    print("wake reason was triggered")

def unique_ids():
    print("unique ids was triggered")


def time_pulse_us(pin, pulse_level, timeout_us=1000000):
    print("time_pulse_us was triggered")

def bitstream(pin, encoding, timing, data):
    print("bitstream was triggered")

def rng():
    print("rng was triggered")

# IRQ wake values
IDLE=0
SLEEP=0
DEEPSLEEP=0

# RESET Causes 
PWRON_RESET=0
HARD_RESET=0
WDT_RESET=0
DEEPSLEEP_RESET=0
SOFT_RESET=0

# Wake-up reasons
WLAN_WAKE=0
PIN_WAKE=0
RTC_WAKE=0


class Pin:
    IN=1
    OUT=3
    OPEN_DRAIN=5
    ALT=7
    ALT_OPEN_DRAIN=9
    ANALOG=2
    PULL_UP=1
    PULL_DOWN=2
    PULL_HOLD=4
    DRIVE_0=0
    DRIVE_1=1
    DRIVE_2=2
    IRQ_FALLING=0x02
    IRQ_RISING=0x01
    IRQ_LOW_LEVEL=0x04
    IRQ_HIGH_LEVEL=0x08

    def __init__(self, id, mode=-1, pull=-1, *, value=None, drive=0, alt=-1):
        self.id = id
        self.mode = mode
        self.pull=pull
        if mode == Pin.OUT or mode == Pin.OPEN_DRAIN:
            self.value = value
        else:
            self.value = None
        self.drive = drive
        self.alt=alt


    def init(self, mode=-1, pull=-1, *, value=None, drive=0, alt=-1):
        self.mode = mode
        self.pull = pull
        self.value = value
        self.drive = drive
        self.alt = alt

    def value(self, val):
        if not val:
            return self.value
        if self.mode == Pin.OUT or self.mode == Pin.OPEN_DRAIN:
            self.value = val
        else:
            return self.value

    def on(self):
        self.value(1)

    def off(self ):
        self.value(0)


    def irq(self,trigger,* ,priority=1, wake=None, hard=False, handler=None):
        pass

    def low(self):
        self.value(0)

    def high(self):
        self.value(0)


    def mode(self, mode):
        if mode:
            self.mode = mode
        else:
            return self.mode

    def pull(self, pull):
        if pull:
            self.pull = pull
        else:
            return self.pull

    def drive(self, drive):
        if drive:
            self.drive = drive
        else:
            return self.drive

    def toggle(self):
        if self.value:
            self.value(0)
        else:
            self.value(1)








