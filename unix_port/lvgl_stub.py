class _Const:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


COLOR_FORMAT = _Const(I1=1)
DISPLAY_RENDER_MODE = _Const(FULL=1)
OPA = _Const(COVER=255)
ALIGN = _Const(TOP_MID=0, CENTER=1, BOTTOM_MID=2)
SYMBOL = _Const(BELL="[bell]", OK="[ok]", WARNING="[warn]")

_default_display = None
_current_screen = None


def init():
    return None


def color_white():
    return 1


def color_black():
    return 0


class _Display:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.flush_cb = None

    def set_color_format(self, fmt):
        _ = fmt

    def set_buffers(self, buf1, buf2, size, mode):
        _ = (buf1, buf2, size, mode)

    def set_default(self):
        global _default_display
        _default_display = self

    def set_flush_cb(self, cb):
        self.flush_cb = cb

    def flush_ready(self):
        return None


class _Widget:
    def __init__(self, parent=None):
        self.parent = parent
        self.text = ""

    def set_size(self, width, height):
        _ = (width, height)

    def set_style_bg_opa(self, opa, part):
        _ = (opa, part)

    def set_style_bg_color(self, color, part):
        _ = (color, part)

    def set_style_text_color(self, color, part):
        _ = (color, part)

    def set_text(self, text):
        self.text = text

    def align(self, align_id, x, y):
        _ = (align_id, x, y)


class obj(_Widget):
    pass


class label(_Widget):
    pass


def display_create(width, height):
    return _Display(width, height)


def screen_load(screen):
    global _current_screen
    _current_screen = screen


def timer_handler():
    return None
