from __future__ import annotations

import pygame

import sim_ui


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
_dirty = True
_text_font = None


def _mark_dirty():
    global _dirty
    _dirty = True


def init():
    return None


def color_white():
    return 1


def color_black():
    return 0


def _as_text_color(value, default=(0, 0, 0)):
    if value is None:
        return default
    # Keep compatibility with this stub's white=1 / black=0 convention.
    return (255, 255, 255) if int(bool(value)) == 1 else (0, 0, 0)


def _as_bg_color(value, default=(255, 255, 255)):
    if value is None:
        return default
    return (255, 255, 255) if int(bool(value)) == 1 else (0, 0, 0)


def _font():
    global _text_font
    if _text_font is None:
        sim_ui.ensure_ui()
        _text_font = pygame.font.Font(None, 12)
    return _text_font


class _Display:
    def __init__(self, width, height):
        self.width = int(width)
        self.height = int(height)
        self.flush_cb = None
        self.buf1 = None
        self.buf2 = None
        self.buf_size = 0
        self.render_mode = None
        self.color_format = None

    def set_color_format(self, fmt):
        self.color_format = fmt

    def set_buffers(self, buf1, buf2, size, mode):
        self.buf1 = buf1
        self.buf2 = buf2
        self.buf_size = int(size)
        self.render_mode = mode
        _mark_dirty()

    def set_default(self):
        global _default_display
        _default_display = self

    def set_flush_cb(self, cb):
        self.flush_cb = cb
        _mark_dirty()

    def flush_ready(self):
        return None


class _Widget:
    def __init__(self, parent=None):
        self.parent = parent
        self.children = []
        self.text = ""
        self.width = None
        self.height = None
        self.bg_opa = None
        self.bg_color = None
        self.text_color = None
        self._align = (ALIGN.CENTER, 0, 0)

        if parent is not None and hasattr(parent, "children"):
            parent.children.append(self)

        _mark_dirty()

    def set_size(self, width, height):
        self.width = int(width)
        self.height = int(height)
        _mark_dirty()

    def set_style_bg_opa(self, opa, part):
        _ = part
        self.bg_opa = opa
        _mark_dirty()

    def set_style_bg_color(self, color, part):
        _ = part
        self.bg_color = color
        _mark_dirty()

    def set_style_text_color(self, color, part):
        _ = part
        self.text_color = color
        _mark_dirty()

    def set_text(self, text):
        self.text = str(text)
        _mark_dirty()

    def align(self, align_id, x, y):
        self._align = (align_id, int(x), int(y))
        _mark_dirty()


class obj(_Widget):
    pass


class label(_Widget):
    pass


def display_create(width, height):
    return _Display(width, height)


def _iter_labels(node):
    if node is None:
        return
    if isinstance(node, label):
        yield node
    for child in getattr(node, "children", ()):
        for item in _iter_labels(child):
            yield item


def _label_position(text_surface, label_obj, width, height):
    tw, th = text_surface.get_size()
    align_id, off_x, off_y = label_obj._align

    if align_id == ALIGN.TOP_MID:
        x = (width - tw) // 2 + off_x
        y = 0 + off_y
    elif align_id == ALIGN.BOTTOM_MID:
        x = (width - tw) // 2 + off_x
        y = (height - th) + off_y
    else:  # ALIGN.CENTER and fallback
        x = (width - tw) // 2 + off_x
        y = (height - th) // 2 + off_y

    return x, y


def _surface_to_i1(surface):
    width, height = surface.get_size()
    stride = (width + 7) // 8
    out = bytearray(8 + stride * height)

    for y in range(height):
        row_base = 8 + y * stride
        for x in range(width):
            r, g, b, _a = surface.get_at((x, y))
            is_dark = (int(r) + int(g) + int(b)) < 384
            if is_dark:
                out[row_base + (x >> 3)] |= 0x80 >> (x & 7)

    return out


def _render_i1_frame(display):
    width = max(1, int(display.width))
    height = max(1, int(display.height))

    surface = pygame.Surface((width, height))
    bg = _as_bg_color(getattr(_current_screen, "bg_color", None), default=(255, 255, 255))
    surface.fill(bg)

    text_font = _font()
    for item in _iter_labels(_current_screen):
        txt = item.text or ""
        if not txt:
            continue
        fg = _as_text_color(item.text_color, default=(0, 0, 0))
        text_surface = text_font.render(txt, True, fg)
        x, y = _label_position(text_surface, item, width, height)
        surface.blit(text_surface, (x, y))

    return _surface_to_i1(surface)


class _ColorPtr:
    def __init__(self, raw):
        self._raw = raw

    def __dereference__(self, length):
        return self._raw[: int(length)]


def screen_load(screen):
    global _current_screen
    _current_screen = screen
    _mark_dirty()


def timer_handler():
    # Desktop simulator must keep pumping events while an LVGL app is active.
    sim_ui.poll_events()

    if not _default_display or not _default_display.flush_cb:
        return

    global _dirty
    if not _dirty:
        return

    raw = _render_i1_frame(_default_display)
    _default_display.flush_cb(_default_display, None, _ColorPtr(raw))
    _dirty = False
