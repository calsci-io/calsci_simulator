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
PART = _Const(MAIN=0x0000, SCROLLBAR=0x0001)
STATE = _Const(DEFAULT=0x0000, CHECKED=0x0100, SCROLLED=0x0200)
SCROLLBAR_MODE = _Const(OFF=0, ON=1, ACTIVE=2)
SYMBOL = _Const(BELL="[bell]", OK="[ok]", WARNING="[warn]")
_OBJ_FLAG = _Const(HIDDEN=0x0001)

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


def _clamp(value, lower, upper):
    return max(lower, min(upper, int(value)))


def _selector(part=PART.MAIN, checked=False):
    if checked:
        return int(part) | int(STATE.CHECKED)
    return int(part)


def _part_only(selector):
    return int(selector) & 0x00FF


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
    FLAG = _OBJ_FLAG

    def __init__(self, parent=None):
        self.parent = parent
        self.children = []
        self.text = ""
        self.width = None
        self.height = None
        self.bg_opa = None
        self.bg_color = None
        self.text_color = None
        self.checked = False
        self.flags = 0
        self._align = (ALIGN.CENTER, 0, 0)
        self._styles = {}

        if parent is not None and hasattr(parent, "children"):
            parent.children.append(self)

        _mark_dirty()

    def _set_style(self, name, value, selector_value):
        bucket = self._styles.setdefault(name, {})
        bucket[int(selector_value)] = value
        _mark_dirty()

    def _get_style(self, name, selector_value, default=None, checked=False):
        bucket = self._styles.get(name, {})
        selector_value = int(selector_value)
        if checked:
            checked_selector = selector_value | int(STATE.CHECKED)
            if checked_selector in bucket:
                return bucket[checked_selector]
        if selector_value in bucket:
            return bucket[selector_value]
        part_only = _part_only(selector_value)
        if part_only in bucket:
            return bucket[part_only]
        if PART.MAIN in bucket:
            return bucket[PART.MAIN]
        return default

    def set_size(self, width, height):
        self.width = int(width)
        self.height = int(height)
        _mark_dirty()

    def set_style_bg_opa(self, opa, part):
        self.bg_opa = opa
        self._set_style("bg_opa", opa, part)

    def set_style_bg_color(self, color, part):
        self.bg_color = color
        self._set_style("bg_color", color, part)

    def set_style_text_color(self, color, part):
        self.text_color = color
        self._set_style("text_color", color, part)

    def set_style_border_width(self, width, part):
        self._set_style("border_width", int(width), part)

    def set_style_border_color(self, color, part):
        self._set_style("border_color", color, part)

    def set_style_radius(self, radius, part):
        self._set_style("radius", int(radius), part)

    def set_style_width(self, width, part):
        self._set_style("width", int(width), part)

    def set_style_pad_right(self, value, part):
        self._set_style("pad_right", int(value), part)

    def set_text(self, text):
        self.text = str(text)
        _mark_dirty()

    def align(self, align_id, x, y):
        self._align = (align_id, int(x), int(y))
        _mark_dirty()

    def add_state(self, state):
        if int(state) & int(STATE.CHECKED):
            self.checked = True
            _mark_dirty()

    def remove_state(self, state):
        if int(state) & int(STATE.CHECKED):
            self.checked = False
            _mark_dirty()

    def get_child(self, index):
        return self.children[int(index)]

    def get_child_count(self):
        return len(self.children)

    def remove_style_all(self):
        self._styles = {}
        _mark_dirty()

    def add_flag(self, flag):
        self.flags |= int(flag)
        _mark_dirty()

    def remove_flag(self, flag):
        self.flags &= ~int(flag)
        _mark_dirty()

    def has_flag(self, flag):
        return bool(self.flags & int(flag))


class obj(_Widget):
    pass


class label(_Widget):
    pass


class button(_Widget):
    def scroll_to_view(self, _anim=False):
        if isinstance(self.parent, list):
            self.parent.scroll_child_into_view(self)

    def scroll_to_view_recursive(self, _anim=False):
        self.scroll_to_view(_anim)


class list(_Widget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scroll_y = 0
        self.scrollbar_mode = SCROLLBAR_MODE.OFF
        self._item_height = 13
        self._item_gap = 1
        self._padding = 1

    def add_button(self, icon, text):
        _ = icon
        btn = button(parent=self)
        lbl = label(parent=btn)
        lbl.set_text(text)
        lbl.align(ALIGN.CENTER, 0, 0)
        _mark_dirty()
        return btn

    def set_scrollbar_mode(self, mode):
        self.scrollbar_mode = mode
        _mark_dirty()

    def _scrollbar_width(self):
        return max(2, int(self._get_style("width", PART.SCROLLBAR, default=3)))

    def _scrollbar_pad_right(self):
        return max(0, int(self._get_style("pad_right", PART.SCROLLBAR, default=0)))

    def _viewport_height(self):
        height = self.height if self.height is not None else 0
        return max(1, int(height) - 2)

    def _content_height(self):
        if not self.children:
            return self._padding * 2
        return (
            self._padding * 2
            + len(self.children) * self._item_height
            + (len(self.children) - 1) * self._item_gap
        )

    def _max_scroll(self):
        return max(0, self._content_height() - self._viewport_height())

    def scroll_child_into_view(self, child):
        try:
            idx = self.children.index(child)
        except ValueError:
            return

        item_top = self._padding + idx * (self._item_height + self._item_gap)
        item_bottom = item_top + self._item_height
        viewport_height = self._viewport_height()

        if item_top < self.scroll_y:
            self.scroll_y = item_top
        elif item_bottom > self.scroll_y + viewport_height:
            self.scroll_y = item_bottom - viewport_height

        self.scroll_y = _clamp(self.scroll_y, 0, self._max_scroll())
        _mark_dirty()


def display_create(width, height):
    return _Display(width, height)


def screen_active():
    return _current_screen


def _widget_rect(node, parent_rect):
    if node.parent is None:
        width = int(node.width) if node.width is not None else int(parent_rect.width)
        height = int(node.height) if node.height is not None else int(parent_rect.height)
        return pygame.Rect(parent_rect.x, parent_rect.y, width, height)

    width = int(node.width) if node.width is not None else int(parent_rect.width)
    height = int(node.height) if node.height is not None else int(parent_rect.height)

    align_id, off_x, off_y = node._align

    if align_id == ALIGN.TOP_MID:
        x = parent_rect.x + (parent_rect.width - width) // 2 + int(off_x)
        y = parent_rect.y + int(off_y)
    elif align_id == ALIGN.BOTTOM_MID:
        x = parent_rect.x + (parent_rect.width - width) // 2 + int(off_x)
        y = parent_rect.bottom - height + int(off_y)
    else:
        x = parent_rect.x + (parent_rect.width - width) // 2 + int(off_x)
        y = parent_rect.y + (parent_rect.height - height) // 2 + int(off_y)

    return pygame.Rect(x, y, width, height)


def _draw_rect(surface, rect, color=None, border_color=None, border_width=0):
    if rect.width <= 0 or rect.height <= 0:
        return
    if color is not None:
        pygame.draw.rect(surface, color, rect)
    if border_width and border_color is not None:
        pygame.draw.rect(surface, border_color, rect, max(1, int(border_width)))


def _draw_label(surface, node, rect, clip_rect=None, fallback_color=None):
    txt = node.text or ""
    if not txt:
        return

    fg = _as_text_color(
        node._get_style("text_color", PART.MAIN, default=fallback_color or node.text_color),
        default=(0, 0, 0),
    )
    text_surface = _font().render(txt, True, fg)
    tw, th = text_surface.get_size()
    align_id, off_x, off_y = node._align

    if align_id == ALIGN.TOP_MID:
        x = rect.x + (rect.width - tw) // 2 + int(off_x)
        y = rect.y + int(off_y)
    elif align_id == ALIGN.BOTTOM_MID:
        x = rect.x + (rect.width - tw) // 2 + int(off_x)
        y = rect.bottom - th + int(off_y)
    else:
        x = rect.x + (rect.width - tw) // 2 + int(off_x)
        y = rect.y + (rect.height - th) // 2 + int(off_y)

    previous_clip = surface.get_clip()
    if clip_rect is not None:
        surface.set_clip(clip_rect)
    surface.blit(text_surface, (x, y))
    surface.set_clip(previous_clip)


def _render_button(surface, node, rect, clip_rect=None):
    checked = bool(node.checked)
    bg = _as_bg_color(
        node._get_style("bg_color", PART.MAIN, default=node.bg_color, checked=checked),
        default=(255, 255, 255),
    )
    border_color = _as_bg_color(
        node._get_style("border_color", PART.MAIN, default=color_black(), checked=checked),
        default=(0, 0, 0),
    )
    border_width = int(node._get_style("border_width", PART.MAIN, default=0, checked=checked) or 0)

    previous_clip = surface.get_clip()
    if clip_rect is not None:
        surface.set_clip(clip_rect)
    _draw_rect(surface, rect, color=bg, border_color=border_color, border_width=border_width)

    if node.children:
        child = node.children[0]
        text_color = node._get_style("text_color", PART.MAIN, default=node.text_color, checked=checked)
        _draw_label(surface, child, rect.inflate(-4, -2), clip_rect=clip_rect, fallback_color=text_color)

    surface.set_clip(previous_clip)


def _render_list(surface, node, rect, clip_rect=None):
    bg = _as_bg_color(node._get_style("bg_color", PART.MAIN, default=node.bg_color), default=(255, 255, 255))
    border_color = _as_bg_color(node._get_style("border_color", PART.MAIN, default=color_black()), default=(0, 0, 0))
    border_width = int(node._get_style("border_width", PART.MAIN, default=0) or 0)
    _draw_rect(surface, rect, color=bg, border_color=border_color, border_width=border_width)

    inner = pygame.Rect(rect.x + 1, rect.y + 1, max(1, rect.width - 2), max(1, rect.height - 2))
    scrollbar_width = node._scrollbar_width()
    scrollbar_gap = node._scrollbar_pad_right()
    scrollbar_x = inner.right - scrollbar_width
    content_width = inner.width - scrollbar_width - scrollbar_gap - 1
    content_width = max(6, content_width)
    viewport = pygame.Rect(inner.x, inner.y, content_width, inner.height)

    previous_clip = surface.get_clip()
    if clip_rect is not None:
        surface.set_clip(clip_rect.clip(viewport))
    else:
        surface.set_clip(viewport)

    y_cursor = inner.y + node._padding - node.scroll_y
    for child in node.children:
        item_rect = pygame.Rect(inner.x + 1, y_cursor, max(4, content_width - 2), node._item_height)
        if item_rect.bottom >= viewport.top and item_rect.top <= viewport.bottom:
            _render_button(surface, child, item_rect, clip_rect=viewport)
        y_cursor += node._item_height + node._item_gap

    surface.set_clip(previous_clip)

    if node.scrollbar_mode != SCROLLBAR_MODE.OFF:
        track_rect = pygame.Rect(scrollbar_x, inner.y, scrollbar_width, inner.height)
        track_color = bg
        _draw_rect(surface, track_rect, color=track_color, border_color=(0, 0, 0), border_width=1)

        content_height = node._content_height()
        if content_height <= inner.height:
            thumb_rect = pygame.Rect(track_rect.x, track_rect.y, track_rect.width, track_rect.height)
        else:
            thumb_height = max(8, int((inner.height * inner.height) / float(content_height)))
            max_scroll = max(1, node._max_scroll())
            thumb_range = max(0, inner.height - thumb_height)
            thumb_y = track_rect.y + int((node.scroll_y / float(max_scroll)) * thumb_range)
            thumb_rect = pygame.Rect(track_rect.x, thumb_y, track_rect.width, thumb_height)
        thumb_color = _as_bg_color(node._get_style("bg_color", PART.SCROLLBAR, default=color_black()), default=(0, 0, 0))
        _draw_rect(surface, thumb_rect, color=thumb_color, border_color=None, border_width=0)


def _render_widget(surface, node, parent_rect, clip_rect=None):
    if node.has_flag(_OBJ_FLAG.HIDDEN):
        return

    rect = _widget_rect(node, parent_rect)

    if isinstance(node, list):
        _render_list(surface, node, rect, clip_rect=clip_rect)
        return

    if isinstance(node, button):
        _render_button(surface, node, rect, clip_rect=clip_rect)
        return

    if isinstance(node, label):
        _draw_label(surface, node, rect, clip_rect=clip_rect)
        return

    bg = node._get_style("bg_color", PART.MAIN, default=node.bg_color)
    bg_opa = node._get_style("bg_opa", PART.MAIN, default=node.bg_opa)
    border_color = _as_bg_color(
        node._get_style("border_color", PART.MAIN, default=color_black()),
        default=(0, 0, 0),
    )
    border_width = int(node._get_style("border_width", PART.MAIN, default=0) or 0)
    if bg_opa == OPA.COVER or node.parent is None:
        _draw_rect(
            surface,
            rect,
            color=_as_bg_color(bg, default=(255, 255, 255)),
            border_color=border_color,
            border_width=border_width,
        )

    for child in node.children:
        _render_widget(surface, child, rect, clip_rect=rect)


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
    bg = (255, 255, 255)
    if _current_screen is not None:
        bg = _as_bg_color(_current_screen._get_style("bg_color", PART.MAIN, default=_current_screen.bg_color), default=bg)
    surface.fill(bg)

    if _current_screen is not None:
        root_rect = pygame.Rect(0, 0, width, height)
        _render_widget(surface, _current_screen, root_rect, clip_rect=root_rect)

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
    sim_ui.poll_events()

    if not _default_display or not _default_display.flush_cb:
        return

    global _dirty
    if not _dirty:
        return

    raw = _render_i1_frame(_default_display)
    _default_display.flush_cb(_default_display, None, _ColorPtr(raw))
    _dirty = False
