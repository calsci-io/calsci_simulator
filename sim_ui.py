from __future__ import annotations

import time
from collections import deque
from pathlib import Path
from typing import Optional

import pygame

# -----------------------------------------------------------------------------
# UI constants (ported from calsci_simulator)
# -----------------------------------------------------------------------------

SCREEN_WIDTH = 450
SCREEN_HEIGHT = 950

DISPLAY_TOP_MARGIN = 85
DISPLAY_BEZEL_PADDING = 16
DISPLAY_SIDE_PADDING = 16

CASE_PADDING = 10
CASE_RADIUS = 32

KEYPAD_TOP_GAP = 14
SYSTEM_TO_MAIN_GAP = 12

CASE_DARK = (24, 26, 30)
CASE_MID = (36, 38, 43)
CASE_LIGHT = (52, 54, 60)
BEZEL_DARK = (22, 23, 27)
BEZEL_MID = (36, 38, 42)
LABEL_BG = (230, 230, 230)
LABEL_TEXT = (40, 40, 40)
LABEL_FONT_SIZE = 16

LCD_ON = (20, 30, 36)
LCD_OFF = (180, 210, 222)

BUTTON_BORDER = (85, 85, 85)
BUTTON_SHADOW = (140, 140, 140)
BUTTON_SHADOW_PRESSED = (95, 95, 95)
BUTTON_BG = (230, 230, 230)
BUTTON_BG_PRESSED = (200, 200, 200)
KEY_TEXT = (0, 0, 0)

# Display geometry
LCD_WIDTH = 128
LCD_HEIGHT = 64
BASE_PIXEL_SIZE = 3
BASE_PIXEL_GAP = 0

# Key layout constants (from calsci_simulator/utility/typer.py)
SYSTEM_KEY = 40
SYSTEM_GAP_X = 12
SYSTEM_GAP_Y = 8

NAV_OK = 50
NAV_LR_W = 50
NAV_LR_H = NAV_LR_W
NAV_GAP = 4
NAV_UD_W = NAV_LR_W
NAV_UD_H = NAV_LR_W
NAV_OFFSET_X = -6
NAV_OFFSET_Y = -2

MAIN_KEY = 50
MAIN_GAP_X = 5
MAIN_GAP_Y = 16

# Matrix pin mapping used by calsci_latest_itr/input_modules/keypad.py
ROW_PINS = [14, 21, 47, 48, 38, 39, 40, 41, 42, 1]
COL_PINS = [8, 18, 17, 15, 7]
KEY_ROWS = 10
KEY_COLS = 5

# Keypad state layouts from calsci_latest_itr/data_modules/keypad_map.py
KEYPAD_DEFAULT = [
    ["on", "alpha", "beta", "home", "wifi"],
    ["backlight", "back", "toolbox", "diff()", "ln()"],
    ["nav_l", "nav_d", "nav_r", "ok", "nav_u"],
    ["module", "bluetooth", "sin()", "cos()", "tan()"],
    ["igtn()", "pi", "e", "summation", "fraction"],
    ["log", "pow(,)", "pow( ,0.5)", "pow( ,2)", "S_D"],
    ["7", "8", "9", "nav_b", "AC"],
    ["4", "5", "6", "*", "/"],
    ["1", "2", "3", "+", "-"],
    [".", "0", ",", "ans", "exe"],
]

KEYPAD_ALPHA = [
    ["on", "alpha", "beta", "home", "wifi"],
    ["backlight", "back", "caps", "f", "l"],
    ["nav_l", "nav_d", "nav_r", "ok", "nav_u"],
    ["a", "b", "c", "d", "e"],
    ["g", "h", "i", "j", "k"],
    ["m", "n", "o", "p", "q"],
    ["r", "s", "t", "nav_b", "AC"],
    ["u", "v", "w", "*", "/"],
    ["x", "y", "z", "+", "-"],
    [" ", "off", "tab", "ans", "exe"],
]

KEYPAD_BETA = [
    ["on", "alpha", "beta", "home", "wifi"],
    ["backlight", "back", "undo", "=", "$"],
    ["nav_l", "nav_d", "nav_r", "ok", "nav_u"],
    ["copy", "paste", "asin(", "acos(", "atan("],
    ["&", "`", '"', "'", "shot"],
    ["^", "~", "!", "<", ">"],
    ["[", "]", "%", "nav_b", "AC"],
    ["{", "}", ":", "*", "/"],
    ["(", ")", ";", "+", "-"],
    ["@", "?", "\"", "ans", "exe"],
]

KEY_SYMBOLS = {
    "rst": "RST",
    "bt": "Boot",
    "on": "ON",
    "alpha": "α",
    "beta": "β",
    "home": "⌂",
    "wifi": "📶",
    "tab": "tab",
    "backlight": "🔆",
    "back": "↩",
    "toolbox": "🧰",
    "diff()": "d/dx",
    "ln()": "ln",
    "module": "|x|",
    "bluetooth": "🅱",
    "sin()": "sin",
    "cos()": "cos",
    "tan()": "tan",
    "asin(": "sin⁻¹",
    "acos(": "cos⁻¹",
    "atan(": "tan⁻¹",
    "igtn()": "∫",
    "pi": "π",
    "summation": "∑",
    "fraction": "a⁄b",
    "log": "log",
    "pow(,)": "xʸ",
    "pow( ,0.5)": "√",
    "pow( ,2)": "x²",
    "S_D": "S↔D",
    "nav_u": "↑",
    "nav_d": "↓",
    "nav_l": "←",
    "nav_r": "→",
    "nav_b": "DEL",
    "ans": "ANS",
    "exe": "EXE",
    "caps": "caps",
    "undo": "undo",
    "copy": "❏",
    "paste": "📋",
    "off": "off",
}

ASSET_CANDIDATES = [
    Path(__file__).resolve().parent / "assets",
    Path(__file__).resolve().parent.parent / "calsci_simulator" / "assets",
]


# Build lookup from key name -> (row, col) in matrix.
KEY_TO_COORD = {}
for _r, _row in enumerate(KEYPAD_DEFAULT):
    for _c, _key in enumerate(_row):
        KEY_TO_COORD[_key] = (_r, _c)


class _KeyWidget:
    def __init__(self, widget, widget_id: int, row: Optional[int], col: Optional[int]):
        self.widget = widget
        self.widget_id = widget_id
        self.row = row
        self.col = col


class _UIState:
    def __init__(self):
        self.initialized = False
        self.screen = None
        self.lcd_surface = None

        self.main_font = None
        self.label_font = None
        self.tiny_label_font = None
        self.fallback_font = None
        self.emoji_font = None
        self._last_scale = None

        self.key_widgets = []
        self.pending_keys = deque()
        self.last_widget_id = None
        self.last_key_ts = 0.0

        self.row_levels = {pin: 1 for pin in ROW_PINS}

        self.framebuffer = bytearray(LCD_WIDTH * LCD_HEIGHT // 8)
        self.invert = False
        self.display_on = True
        self.all_points_on = False

        self.dirty = True
        self.last_render = 0.0
        self.click_sound = None
        self.click_sound_ready = False


STATE = _UIState()


def _load_font(name: str, size: int):
    for candidate in ASSET_CANDIDATES:
        path = candidate / name
        if path.exists():
            return pygame.font.Font(str(path), size)
    return pygame.font.Font(None, size)


def _load_click_sound():
    if STATE.click_sound_ready:
        return STATE.click_sound

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        for candidate in ASSET_CANDIDATES:
            sound_path = candidate / "click.wav"
            if sound_path.exists():
                STATE.click_sound = pygame.mixer.Sound(str(sound_path))
                STATE.click_sound.set_volume(0.4)
                break
    except Exception:
        STATE.click_sound = None

    STATE.click_sound_ready = True
    return STATE.click_sound


def _play_click():
    sound = _load_click_sound()
    if sound:
        try:
            sound.play()
        except Exception:
            pass


def get_scale(screen):
    width, height = screen.get_size()
    if width <= 0 or height <= 0:
        return 1.0
    return min(width / SCREEN_WIDTH, height / SCREEN_HEIGHT)


def scale_value(value, screen, min_value=0):
    scaled = int(round(value * get_scale(screen)))
    return max(min_value, scaled)


def _display_metrics(screen):
    box = scale_value(BASE_PIXEL_SIZE, screen, min_value=1)
    gap = scale_value(BASE_PIXEL_GAP, screen, min_value=0)
    display_w = LCD_WIDTH * (box + gap)
    display_h = LCD_HEIGHT * (box + gap)
    return box, gap, display_w, display_h


def _display_rect(screen):
    _, _, display_w, display_h = _display_metrics(screen)
    x = (screen.get_width() - display_w) // 2
    y = scale_value(DISPLAY_TOP_MARGIN, screen, min_value=0)
    return pygame.Rect(x, y, display_w, display_h)


def _symbol(key: str):
    return KEY_SYMBOLS.get(key, key)


def _ensure_fonts(scale):
    if STATE._last_scale == scale:
        return

    main_size = max(8, int(round(14 * scale)))
    label_size = max(7, int(round(12 * scale)))
    tiny_size = max(6, int(round(9 * scale)))

    STATE.main_font = _load_font("DejaVuSans.ttf", main_size)
    STATE.label_font = _load_font("DejaVuSans.ttf", label_size)
    STATE.tiny_label_font = _load_font("DejaVuSans.ttf", tiny_size)
    STATE.fallback_font = _load_font("notosymbols2.ttf", main_size)
    STATE.emoji_font = _load_font("notoemoji.ttf", main_size)
    STATE._last_scale = scale


def _font_for_text(text, tiny=False, small=False):
    if tiny:
        font = STATE.tiny_label_font
    else:
        font = STATE.label_font if small else STATE.main_font

    try:
        metrics = font.metrics(text)
    except Exception:
        metrics = None

    if metrics is None or any(m is None for m in metrics):
        font = STATE.fallback_font

    if text in {"📶", "🔆", "🧰", "🅱", "📋", "❏"}:
        font = STATE.emoji_font

    return font


def _draw_shell(screen):
    w, h = screen.get_size()

    screen.fill(CASE_DARK)

    case_padding = scale_value(CASE_PADDING, screen, min_value=0)
    case_radius = scale_value(CASE_RADIUS, screen, min_value=0)
    outer = pygame.Rect(case_padding, case_padding, w - 2 * case_padding, h - 2 * case_padding)
    pygame.draw.rect(screen, CASE_DARK, outer, border_radius=case_radius)

    mid = outer.inflate(-scale_value(8, screen, min_value=0), -scale_value(8, screen, min_value=0))
    pygame.draw.rect(screen, CASE_MID, mid, border_radius=max(0, case_radius - scale_value(6, screen, min_value=0)))

    inner = mid.inflate(-scale_value(6, screen, min_value=0), -scale_value(6, screen, min_value=0))
    pygame.draw.rect(screen, CASE_LIGHT, inner, border_radius=max(0, case_radius - scale_value(10, screen, min_value=0)))

    label_w = scale_value(90, screen, min_value=1)
    label_h = scale_value(26, screen, min_value=1)
    label_x = w // 2 - label_w // 2
    label_y = case_padding + scale_value(8, screen, min_value=0)
    label_radius = scale_value(6, screen, min_value=0)
    pygame.draw.rect(screen, LABEL_BG, (label_x, label_y, label_w, label_h), border_radius=label_radius)

    brand_font = _load_font("DejaVuSans.ttf", max(8, scale_value(LABEL_FONT_SIZE, screen, min_value=1)))
    text = brand_font.render("CalSci", True, LABEL_TEXT)
    screen.blit(text, text.get_rect(center=(label_x + label_w // 2, label_y + label_h // 2)))

    disp = _display_rect(screen)
    bezel_pad = scale_value(DISPLAY_BEZEL_PADDING, screen, min_value=0)
    bezel = disp.inflate(bezel_pad * 2, bezel_pad * 2)
    bezel_radius = scale_value(14, screen, min_value=0)
    pygame.draw.rect(screen, BEZEL_MID, bezel, border_radius=bezel_radius)
    pygame.draw.rect(screen, BEZEL_DARK, bezel, width=2, border_radius=bezel_radius)

    shadow = bezel.move(0, scale_value(3, screen, min_value=0))
    pygame.draw.rect(screen, (18, 19, 21), shadow, width=2, border_radius=bezel_radius)


class Button:
    def __init__(self, text, width, height, pos_x, pos_y, shape="rect"):
        self.text = text
        self.width = width
        self.height = height
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.shape = shape
        self.rect = pygame.Rect(pos_x, pos_y, width, height)

    def draw(self, screen, pressed=False):
        radius = min(self.width, self.height) // 2 if self.shape == "circle" else max(4, min(10, self.height // 5))

        shadow_color = BUTTON_SHADOW_PRESSED if pressed else BUTTON_SHADOW
        border_color = (55, 55, 55) if pressed else BUTTON_BORDER
        base_color = BUTTON_BG_PRESSED if pressed else BUTTON_BG
        shadow_offset = 0 if pressed else 2
        text_offset = max(1, int(round(2 * get_scale(screen)))) if pressed else 0

        shadow_rect = self.rect.move(0, shadow_offset)
        pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=radius)
        pygame.draw.rect(screen, base_color, self.rect, border_radius=radius)
        pygame.draw.rect(screen, border_color, self.rect, width=1, border_radius=radius)

        font = _font_for_text(self.text)
        text = font.render(self.text, True, KEY_TEXT)
        text_rect = text.get_rect(center=(self.rect.centerx, self.rect.centery + text_offset))
        screen.blit(text, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class OtherButton(Button):
    def __init__(self, text, alpha_text, beta_text, width, height, pos_x, pos_y):
        super().__init__(text=text, width=width, height=height, pos_x=pos_x, pos_y=pos_y, shape="rect")
        self.alpha_text = alpha_text
        self.beta_text = beta_text

    def draw(self, screen, pressed=False):
        radius = max(4, min(10, self.height // 5))
        shadow_color = BUTTON_SHADOW_PRESSED if pressed else BUTTON_SHADOW
        border_color = (55, 55, 55) if pressed else BUTTON_BORDER
        base_color = BUTTON_BG_PRESSED if pressed else BUTTON_BG
        shadow_offset = 0 if pressed else 2
        text_offset = max(1, int(round(2 * get_scale(screen)))) if pressed else 0

        shadow_rect = self.rect.move(0, shadow_offset)
        pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=radius)
        pygame.draw.rect(screen, base_color, self.rect, border_radius=radius)
        pygame.draw.rect(screen, border_color, self.rect, width=1, border_radius=radius)

        pad = max(2, int(round(4 * get_scale(screen))))

        if self.alpha_text:
            alpha_tiny = self.alpha_text.lower() in {"caps", "undo"}
            alpha_font = _font_for_text(self.alpha_text, small=True, tiny=alpha_tiny)
            alpha = alpha_font.render(self.alpha_text, True, KEY_TEXT)
            alpha_rect = alpha.get_rect(topleft=(self.pos_x + pad, self.pos_y + pad + text_offset))
            screen.blit(alpha, alpha_rect)

        if self.beta_text:
            beta_tiny = self.beta_text.lower() in {"caps", "undo"}
            beta_font = _font_for_text(self.beta_text, small=True, tiny=beta_tiny)
            beta = beta_font.render(self.beta_text, True, KEY_TEXT)
            beta_rect = beta.get_rect(topright=(self.pos_x + self.width - pad, self.pos_y + pad + text_offset))
            screen.blit(beta, beta_rect)

        main_font = _font_for_text(self.text)
        main = main_font.render(self.text, True, KEY_TEXT)
        main_rect = main.get_rect(midbottom=(self.pos_x + self.width // 2, self.pos_y + self.height - pad + text_offset))
        screen.blit(main, main_rect)


def _alpha_beta_labels_for(default_key: str):
    coord = KEY_TO_COORD.get(default_key)
    if coord is None:
        return "", ""

    row, col = coord
    alpha = KEYPAD_ALPHA[row][col]
    beta = KEYPAD_BETA[row][col]

    alpha_label = _symbol(alpha) if alpha != default_key else ""
    beta_label = _symbol(beta) if beta != default_key else ""
    return alpha_label, beta_label


def _build_key_widgets(screen):
    _, _, display_w, display_h = _display_metrics(screen)
    screen_w = screen.get_width()

    left_margin = (screen_w - display_w) // 2
    display_bottom = (
        scale_value(DISPLAY_TOP_MARGIN, screen, min_value=0)
        + display_h
        + scale_value(DISPLAY_BEZEL_PADDING, screen, min_value=0) * 2
    )
    top_start = display_bottom + scale_value(KEYPAD_TOP_GAP, screen, min_value=0)

    widgets = []
    wid = 0

    def add_button(key, x, y, width, height, shape="rect", other=False, row=None, col=None):
        nonlocal wid
        label = _symbol(key)
        mapped_row, mapped_col = row, col
        if mapped_row is None or mapped_col is None:
            coord = KEY_TO_COORD.get(key)
            if coord is not None:
                mapped_row, mapped_col = coord

        if other:
            alpha_label, beta_label = _alpha_beta_labels_for(key)
            btn = OtherButton(label, alpha_label, beta_label, width, height, x, y)
        else:
            btn = Button(label, width, height, x, y, shape=shape)

        widgets.append(_KeyWidget(btn, wid, mapped_row, mapped_col))
        wid += 1

    # ---------------- System + Nav clusters ----------------
    system_h = scale_value(SYSTEM_KEY, screen, min_value=1)
    system_w = system_h
    system_gap_x = scale_value(SYSTEM_GAP_X, screen, min_value=1)
    system_gap_y = scale_value(SYSTEM_GAP_Y, screen, min_value=1)

    system_cols = 3
    system_width = system_cols * system_w + (system_cols - 1) * system_gap_x

    nav_ok_size = scale_value(NAV_OK, screen, min_value=1)
    nav_lr_w = scale_value(NAV_LR_W, screen, min_value=1)
    nav_lr_h = scale_value(NAV_LR_H, screen, min_value=1)
    nav_gap = scale_value(NAV_GAP, screen, min_value=1)
    nav_ud_w = scale_value(NAV_UD_W, screen, min_value=1)
    nav_ud_h = scale_value(NAV_UD_H, screen, min_value=1)
    nav_width = nav_lr_w + nav_gap + nav_ok_size + nav_gap + nav_lr_w
    nav_height = nav_ud_h + nav_gap + nav_ok_size + nav_gap + nav_ud_h

    top_gap = display_w - system_width - nav_width
    top_gap = max(top_gap, system_gap_x)
    system_start_x = left_margin
    nav_left_edge = system_start_x + system_width + top_gap + scale_value(NAV_OFFSET_X, screen, min_value=-1000)
    system_block_h = 3 * system_h + 2 * system_gap_y
    system_y_start = top_start
    nav_top_edge = system_y_start + (system_block_h - nav_height) // 2 + scale_value(NAV_OFFSET_Y, screen, min_value=-1000)

    nav_ok_x = nav_left_edge + nav_lr_w + nav_gap
    nav_ok_y = nav_top_edge + nav_ud_h + nav_gap
    nav_ud_x = nav_left_edge + (nav_width - nav_ud_w) // 2
    nav_lr_y = nav_ok_y + (nav_ok_size - nav_lr_h) // 2

    add_button("ok", nav_ok_x, nav_ok_y, nav_ok_size, nav_ok_size)
    add_button("nav_u", nav_ud_x, nav_top_edge, nav_ud_w, nav_ud_h)
    add_button("nav_d", nav_ud_x, nav_ok_y + nav_ok_size + nav_gap, nav_ud_w, nav_ud_h)
    add_button("nav_l", nav_left_edge, nav_lr_y, nav_lr_w, nav_lr_h)
    add_button("nav_r", nav_left_edge + nav_lr_w + nav_gap + nav_ok_size + nav_gap, nav_lr_y, nav_lr_w, nav_lr_h)

    system_rows = [
        ["on", "rst", "bt"],
        ["alpha", "beta", "home"],
        ["back", "backlight", "wifi"],
    ]

    for i, row_keys in enumerate(system_rows):
        y = system_y_start + (system_h + system_gap_y) * i
        for j, key in enumerate(row_keys):
            x = system_start_x + j * (system_w + system_gap_x)
            shape = "circle" if key in {"rst", "bt"} else "rect"
            add_button(key, x, y, system_w, system_h, shape=shape)

    # ---------------- Main sections ----------------
    main_h = scale_value(MAIN_KEY, screen, min_value=1)
    main_w = main_h
    main_gap_x = scale_value(MAIN_GAP_X, screen, min_value=1)
    main_gap_y = scale_value(MAIN_GAP_Y, screen, min_value=1)

    section_1_layouts = [
        ["toolbox", "module", "bluetooth", "sin()", "cos()", "tan()"],
        ["diff()", "igtn()", "pi", "e", "summation", "fraction"],
        ["ln()", "log", "pow(,)", "pow( ,0.5)", "pow( ,2)", "S_D"],
    ]

    section_2_layouts = [
        ["7", "8", "9", "nav_b", "AC"],
        ["4", "5", "6", "*", "/"],
        ["1", "2", "3", "+", "-"],
        [".", "0", ",", "ans", "exe"],
    ]

    section_1_gap_x = max(int((display_w - (6 * main_w)) / 5), main_gap_x)
    section_1_y_start = top_start + system_block_h + scale_value(SYSTEM_TO_MAIN_GAP, screen, min_value=0)

    for i, row_keys in enumerate(section_1_layouts):
        y = section_1_y_start + i * (main_h + main_gap_y)
        for j, key in enumerate(row_keys):
            x = left_margin + j * (main_w + section_1_gap_x)
            add_button(key, x, y, main_w, main_h, other=True)

    section_2_y_start = int(section_1_y_start + 3.0 * (main_h + main_gap_y))
    for i, row_keys in enumerate(section_2_layouts):
        y = section_2_y_start + i * (main_h + main_gap_y)
        section_2_gap_x = max(int((display_w - (5 * main_w)) / 4), main_gap_x + scale_value(20, screen, min_value=0))
        for j, key in enumerate(row_keys):
            x = left_margin + j * (main_w + section_2_gap_x)
            add_button(key, x, y, main_w, main_h, other=True)

    return widgets


def ensure_ui():
    if STATE.initialized:
        return

    pygame.init()
    pygame.font.init()

    STATE.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("CalSci Latest ITR Simulator")
    STATE.lcd_surface = pygame.Surface((LCD_WIDTH, LCD_HEIGHT))

    _ensure_fonts(get_scale(STATE.screen))
    STATE.key_widgets = _build_key_widgets(STATE.screen)

    STATE.initialized = True
    render(force=True)


def _queue_key(row_idx: int, col_idx: int, widget_id: Optional[int] = None):
    _play_click()
    STATE.pending_keys.append((row_idx, col_idx))
    STATE.last_widget_id = widget_id
    STATE.last_key_ts = time.monotonic()


def _keyboard_shortcuts():
    return {
        pygame.K_RETURN: (2, 3),
        pygame.K_BACKSPACE: (1, 1),
        pygame.K_ESCAPE: (0, 3),
        pygame.K_UP: (2, 4),
        pygame.K_DOWN: (2, 1),
        pygame.K_LEFT: (2, 0),
        pygame.K_RIGHT: (2, 2),
    }


def poll_events():
    ensure_ui()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit(0)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for item in STATE.key_widgets:
                if item.widget.is_clicked(event.pos):
                    if item.row is not None and item.col is not None:
                        _queue_key(item.row, item.col, widget_id=item.widget_id)
                    else:
                        _play_click()
                        STATE.last_widget_id = item.widget_id
                        STATE.last_key_ts = time.monotonic()
                    break

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q and (event.mod & pygame.KMOD_CTRL):
                raise SystemExit(0)
            shortcut = _keyboard_shortcuts().get(event.key)
            if shortcut:
                _queue_key(shortcut[0], shortcut[1], widget_id=None)

    if STATE.dirty or (time.monotonic() - STATE.last_key_ts) < 0.15:
        render(force=False)


def set_row_level(pin: int, value: int):
    STATE.row_levels[pin] = 1 if value else 0


def read_col_pin(col_pin: int) -> int:
    poll_events()

    if not STATE.pending_keys:
        return 1

    row_idx, col_idx = STATE.pending_keys[0]
    expected_col_pin = COL_PINS[col_idx]
    expected_row_pin = ROW_PINS[row_idx]

    if col_pin != expected_col_pin:
        return 1

    if STATE.row_levels.get(expected_row_pin, 1) == 0:
        STATE.pending_keys.popleft()
        return 0

    return 1


def clear_keys():
    STATE.pending_keys.clear()


def request_render():
    STATE.dirty = True


def set_invert(enabled: bool):
    STATE.invert = bool(enabled)
    STATE.dirty = True


def set_display_on(enabled: bool):
    STATE.display_on = bool(enabled)
    STATE.dirty = True


def set_all_points_on(enabled: bool):
    STATE.all_points_on = bool(enabled)
    STATE.dirty = True


def clear_framebuffer():
    STATE.framebuffer[:] = b"\x00" * len(STATE.framebuffer)
    STATE.dirty = True


def set_framebuffer(data):
    data = bytes(data)
    STATE.framebuffer[:] = data[: len(STATE.framebuffer)]
    STATE.dirty = True


def write_page_byte(page: int, col: int, value: int):
    if not (0 <= page < 8 and 0 <= col < LCD_WIDTH):
        return
    STATE.framebuffer[page * LCD_WIDTH + col] = value & 0xFF
    STATE.dirty = True


def _draw_lcd_pixels():
    for x in range(LCD_WIDTH):
        for page in range(8):
            value = STATE.framebuffer[page * LCD_WIDTH + x]
            y_base = page * 8
            for bit in range(8):
                on = (value >> bit) & 0x01
                if STATE.all_points_on:
                    on = 1
                if STATE.invert:
                    on = 0 if on else 1
                color = LCD_ON if (STATE.display_on and on) else LCD_OFF
                STATE.lcd_surface.set_at((x, y_base + bit), color)


def render(force: bool = False):
    ensure_ui()

    now = time.monotonic()
    if not force and not STATE.dirty:
        return
    if not force and (now - STATE.last_render) < (1.0 / 60.0):
        return

    _ensure_fonts(get_scale(STATE.screen))
    _draw_shell(STATE.screen)
    _draw_lcd_pixels()

    disp = _display_rect(STATE.screen)
    scaled_lcd = pygame.transform.scale(STATE.lcd_surface, (disp.width, disp.height))
    STATE.screen.blit(scaled_lcd, (disp.x, disp.y))

    for item in STATE.key_widgets:
        pressed = (STATE.last_widget_id == item.widget_id) and ((now - STATE.last_key_ts) < 0.15)
        item.widget.draw(STATE.screen, pressed=pressed)

    pygame.display.flip()
    STATE.last_render = now
    STATE.dirty = False
