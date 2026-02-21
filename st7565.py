from __future__ import annotations

import sim_ui

_DISPLAY_WIDTH = 128
_DISPLAY_HEIGHT = 64
_PAGE_COUNT = 8
# ST7565 controller RAM is 132 columns wide, while only 128 are visible.
_RAM_WIDTH = 132

_page = 0
_col = 0
_expect_contrast = False
_contrast = 32


def init(*_pins):
    sim_ui.ensure_ui()
    sim_ui.request_render()


def set_page_address(page: int):
    global _page
    _page = max(0, min(_PAGE_COUNT - 1, int(page)))


def set_column_address(col: int):
    global _col
    _col = max(0, min(_RAM_WIDTH - 1, int(col)))


def _consume_contrast_if_needed(value: int):
    global _expect_contrast
    if _expect_contrast:
        set_contrast(value)
        _expect_contrast = False
        return True
    return False


def write_instruction(cmd: int):
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


def write_data(data: int):
    global _col
    sim_ui.poll_events()
    # Writes beyond visible 128 columns are accepted by controller RAM but hidden.
    if 0 <= _col < _DISPLAY_WIDTH:
        sim_ui.write_page_byte(_page, _col, int(data) & 0xFF)
    _col = (_col + 1) % _RAM_WIDTH


def clear_display():
    sim_ui.clear_framebuffer()


def set_contrast(value: int):
    global _contrast
    _contrast = int(value) & 0x3F


def invert(enabled: bool):
    sim_ui.set_invert(bool(enabled))


def set_inverse(enabled: bool):
    invert(enabled)


def all_points_on(enabled: bool):
    sim_ui.set_all_points_on(bool(enabled))


def off():
    sim_ui.set_display_on(False)


def on():
    sim_ui.set_display_on(True)


def graphics(framebuffer):
    sim_ui.poll_events()

    if hasattr(framebuffer, "buffer"):
        raw = framebuffer.buffer
    else:
        raw = framebuffer

    try:
        data = bytes(raw)
    except Exception:
        return

    target_size = _DISPLAY_WIDTH * _DISPLAY_HEIGHT // 8
    if len(data) < target_size:
        data = data + b"\x00" * (target_size - len(data))
    sim_ui.set_framebuffer(data[:target_size])


# Some code conditionally inspects this attribute.
graphics.pixels_changed = 0
