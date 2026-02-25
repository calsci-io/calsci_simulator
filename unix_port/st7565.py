_DISPLAY_WIDTH = 128
_DISPLAY_HEIGHT = 64
_PAGE_COUNT = 8
_RAM_WIDTH = 132

width = _DISPLAY_WIDTH
height = _DISPLAY_HEIGHT

buffer = bytearray(_DISPLAY_WIDTH * _PAGE_COUNT)

_page = 0
_col = 0
_expect_contrast = False
_contrast = 32
_display_on = True
_inverted = False
_all_points_on = False


def init(*_pins):
    clear_display()


def set_page_address(page):
    global _page
    page = int(page)
    if page < 0:
        page = 0
    if page >= _PAGE_COUNT:
        page = _PAGE_COUNT - 1
    _page = page


def set_column_address(col):
    global _col
    col = int(col)
    if col < 0:
        col = 0
    if col >= _RAM_WIDTH:
        col = _RAM_WIDTH - 1
    _col = col


def _consume_contrast_if_needed(value):
    global _expect_contrast
    if _expect_contrast:
        set_contrast(value)
        _expect_contrast = False
        return True
    return False


def write_instruction(cmd):
    global _col, _expect_contrast

    cmd = int(cmd) & 0xFF

    if _consume_contrast_if_needed(cmd):
        return

    if 0xB0 <= cmd <= 0xB7:
        set_page_address(cmd - 0xB0)
        return

    if 0x10 <= cmd <= 0x1F:
        _col = ((_col & 0x0F) | ((cmd & 0x0F) << 4)) % _RAM_WIDTH
        return

    if 0x00 <= cmd <= 0x0F:
        _col = ((_col & 0xF0) | (cmd & 0x0F)) % _RAM_WIDTH
        return

    if cmd == 0xA7:
        invert(True)
        return
    if cmd == 0xA6:
        invert(False)
        return
    if cmd == 0xA5:
        all_points_on(True)
        return
    if cmd == 0xA4:
        all_points_on(False)
        return
    if cmd == 0xAE:
        off()
        return
    if cmd == 0xAF:
        on()
        return
    if cmd == 0x81:
        _expect_contrast = True


def _write_page_byte(page, col, value):
    if page < 0 or page >= _PAGE_COUNT:
        return
    if col < 0 or col >= _DISPLAY_WIDTH:
        return
    buffer[page * _DISPLAY_WIDTH + col] = int(value) & 0xFF


def write_data(data):
    global _col
    if 0 <= _col < _DISPLAY_WIDTH:
        _write_page_byte(_page, _col, data)
    _col = (_col + 1) % _RAM_WIDTH


def clear_display():
    for i in range(len(buffer)):
        buffer[i] = 0


def set_contrast(value):
    global _contrast
    _contrast = int(value) & 0x3F


def invert(enabled):
    global _inverted
    _inverted = bool(enabled)


def set_inverse(enabled):
    invert(enabled)


def all_points_on(enabled):
    global _all_points_on
    _all_points_on = bool(enabled)


def off():
    global _display_on
    _display_on = False


def on():
    global _display_on
    _display_on = True


def show():
    return None


def fill(value):
    byte = 0xFF if value else 0x00
    for i in range(len(buffer)):
        buffer[i] = byte


def pixel(x, y, color=1):
    x = int(x)
    y = int(y)

    if x < 0 or y < 0 or x >= _DISPLAY_WIDTH or y >= _DISPLAY_HEIGHT:
        return

    page = y >> 3
    bit = 1 << (y & 7)
    idx = page * _DISPLAY_WIDTH + x

    if color:
        buffer[idx] |= bit
    else:
        buffer[idx] &= (0xFF ^ bit)


def _graphics_impl(framebuffer, page=0, column=0, width=None, pages=None):
    if width is None:
        width = _DISPLAY_WIDTH
    if pages is None:
        pages = _PAGE_COUNT

    page = int(page)
    column = int(column)
    width = int(width)
    pages = int(pages)

    if page < 0 or page >= _PAGE_COUNT:
        raise ValueError("page out of range")
    if column < 0 or column >= _DISPLAY_WIDTH:
        raise ValueError("column out of range")
    if width <= 0 or width > _DISPLAY_WIDTH:
        raise ValueError("width out of range")
    if pages <= 0 or pages > _PAGE_COUNT:
        raise ValueError("pages out of range")
    if column + width > _DISPLAY_WIDTH:
        raise ValueError("column + width exceeds display")
    if page + pages > _PAGE_COUNT:
        raise ValueError("page + pages exceeds display")

    raw = framebuffer
    if hasattr(framebuffer, "buffer"):
        raw = framebuffer.buffer

    try:
        data = bytes(raw)
    except Exception:
        return

    expected_size = width * pages
    if len(data) < expected_size:
        data = data + b"\x00" * (expected_size - len(data))
    elif len(data) > expected_size:
        data = data[:expected_size]

    idx = 0
    for page_idx in range(page, page + pages):
        base = page_idx * _DISPLAY_WIDTH
        for col_idx in range(column, column + width):
            buffer[base + col_idx] = data[idx]
            idx += 1


class _GraphicsCallable:
    def __init__(self):
        self.pixels_changed = 0

    def __call__(self, framebuffer, page=0, column=0, width=None, pages=None):
        return _graphics_impl(framebuffer, page=page, column=column, width=width, pages=pages)


graphics = _GraphicsCallable()


def get_buffer():
    return bytes(buffer)
