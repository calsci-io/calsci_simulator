from __future__ import annotations

import time
from collections import deque
from pathlib import Path
from typing import Optional

import pygame

# -----------------------------------------------------------------------------
# UI constants (ported from calsci_simulator)
# -----------------------------------------------------------------------------

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 900

REFERENCE_WIDTH = 900
REFERENCE_HEIGHT = 1350

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

LCD_ON = (24, 24, 24)
LCD_OFF = (105, 106, 104)
LCD_OFF_BACKGROUND = (92, 92, 92)
KEY_WELL_BG = (238, 238, 236)
KEY_PRESS_FILL = (219, 219, 217)
KEY_PRESS_BORDER = (108, 108, 108)
KEY_PRESS_HILITE = (247, 247, 246)
KEY_PRESS_SHADE = (118, 118, 118)

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
    ["on", "home", "settings", "back", "lock"],
    ["beta", "alpha", "toolbox", "fraction", "F1"],
    ["nav_l", "nav_d", "nav_r", "ok", "nav_u"],
    ["pi", "log", "sin", "cos", "tan"],
    ["pow", "root", ",", "(", ")"],
    ["F2", "F3", "F4", "F5", "F6"],
    ["7", "8", "9", "nav_b", "AC"],
    ["4", "5", "6", "*", "/"],
    ["1", "2", "3", "+", "-"],
    [".", "0", "*pow(10, )", "ans", "exe"],
]

KEYPAD_ALPHA = [
    ["on", "home", "settings", "back", "lock"],
    ["beta", "alpha", "caps", "f", "l"],
    ["nav_l", "nav_d", "nav_r", "ok", "nav_u"],
    ["a", "b", "c", "d", "e"],
    ["g", "h", "i", "j", "k"],
    ["m", "n", "o", "p", "q"],
    ["r", "s", "t", "nav_b", "AC"],
    ["u", "v", "w", "*", "/"],
    ["x", "y", "z", "+", "-"],
    ["tab", " ", "", "ans", "exe"],
]

KEYPAD_BETA = [
    ["on", "home", "settings", "back", "lock"],
    ["beta", "alpha", "undo", "=", "$"],
    ["nav_l", "nav_d", "nav_r", "ok", "nav_u"],
    ["copy", "paste", "asin", "acos", "atan"],
    ["&", "`", '"', "'", "\\"],
    ["^", "~", "!", "<", ">"],
    ["[", "]", "%", "nav_b", "AC"],
    ["{", "}", ":", "*", "/"],
    ["#", "|", ";", "+", "-"],
    ["@", "?", "_", "ans", "exe"],
]

KEY_SYMBOLS = {
    "rst": "RST",
    "bt": "Boot",
    "on": "ON",
    "beta": "β",
    "alpha": "α",
    "home": "⌂",
    "settings": "SET",
    "back": "↩",
    "lock": "lock",
    "wifi": "📶",
    "tab": "tab",
    "backlight": "🔆",
    "toolbox": "🧰",
    "fraction": "a⁄b",
    "F1": "F1",
    "sin": "sin",
    "cos": "cos",
    "tan": "tan",
    "asin": "asin",
    "acos": "acos",
    "atan": "atan",
    "pi": "π",
    "log": "log",
    "pow": "xʸ",
    "root": "√",
    "F2": "F2",
    "F3": "F3",
    "F4": "F4",
    "F5": "F5",
    "F6": "F6",
    "nav_u": "↑",
    "nav_d": "↓",
    "nav_l": "←",
    "nav_r": "→",
    "nav_b": "DEL",
    "*pow(10, )": "x10",
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
BACKGROUND_CANDIDATES = [
    Path(__file__).resolve().parent / "Untitled.jpeg",
    Path(__file__).resolve().parent / "Untitled.jpg",
]
SCREENSHOT_DIR = Path(__file__).resolve().parent.parent / "simulator_screen_shots"

# Active LCD plane measured from the inner sharp-edged screen cutout
# in the reference mockup, not the rounded outer display bezel.
REFERENCE_DISPLAY_RECT = (191, 150, 508, 264)

# Background-aligned hitboxes over the reference mockup.
IMAGE_BUTTON_LAYOUT = [
    ("on", (176, 536, 73, 44), "rect"),
    ("rst", (258, 530, 56, 56), "circle"),
    ("bt", (321, 530, 56, 56), "circle"),
    ("nav_u", (543, 531, 87, 55), "rect"),
    ("home", (176, 618, 73, 44), "rect"),
    ("settings", (270, 618, 73, 44), "rect"),
    ("back", (364, 618, 72, 44), "rect"),
    ("nav_l", (480, 593, 56, 87), "rect"),
    ("ok", (551, 601, 71, 71), "circle"),
    ("nav_r", (637, 593, 56, 87), "rect"),
    ("alpha", (176, 692, 73, 44), "rect"),
    ("beta", (270, 692, 72, 44), "rect"),
    ("lock", (363, 692, 72, 44), "rect"),
    ("nav_d", (543, 687, 87, 56), "rect"),
    ("toolbox", (176, 775, 73, 44), "rect"),
    ("pi", (270, 775, 72, 44), "rect"),
    ("log", (363, 775, 73, 44), "rect"),
    ("sin", (457, 775, 72, 44), "rect"),
    ("cos", (551, 775, 71, 44), "rect"),
    ("tan", (644, 775, 71, 44), "rect"),
    ("fraction", (176, 846, 73, 45), "rect"),
    ("pow", (271, 846, 71, 45), "rect"),
    ("root", (364, 846, 72, 44), "rect"),
    (",", (457, 846, 72, 44), "rect"),
    ("(", (551, 846, 71, 44), "rect"),
    (")", (644, 846, 71, 44), "rect"),
    ("F1", (176, 916, 73, 44), "rect"),
    ("F2", (270, 916, 72, 44), "rect"),
    ("F3", (363, 916, 73, 44), "rect"),
    ("F4", (457, 916, 72, 44), "rect"),
    ("F5", (551, 916, 71, 44), "rect"),
    ("F6", (644, 916, 71, 44), "rect"),
    ("7", (176, 986, 87, 52), "rect"),
    ("8", (289, 986, 87, 52), "rect"),
    ("9", (402, 986, 87, 52), "rect"),
    ("nav_b", (515, 986, 87, 52), "rect"),
    ("AC", (627, 986, 87, 52), "rect"),
    ("4", (176, 1057, 87, 51), "rect"),
    ("5", (289, 1057, 87, 51), "rect"),
    ("6", (402, 1057, 87, 51), "rect"),
    ("*", (515, 1057, 87, 51), "rect"),
    ("/", (627, 1057, 87, 51), "rect"),
    ("1", (176, 1127, 87, 52), "rect"),
    ("2", (289, 1127, 87, 52), "rect"),
    ("3", (402, 1127, 87, 52), "rect"),
    ("+", (515, 1127, 87, 52), "rect"),
    ("-", (627, 1127, 87, 52), "rect"),
    (".", (176, 1204, 87, 46), "rect"),
    ("0", (289, 1204, 87, 46), "rect"),
    ("*pow(10, )", (402, 1204, 87, 46), "rect"),
    ("ans", (515, 1204, 87, 46), "rect"),
    ("exe", (627, 1204, 87, 46), "rect"),
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
        self.background_surface = None
        self.background_scaled = None
        self.background_rect = None
        self.background_scale_key = None

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

PRESS_HOLD_SECS = 0.05
PRESS_RELEASE_SECS = 0.10
PRESS_TOTAL_SECS = PRESS_HOLD_SECS + PRESS_RELEASE_SECS
RELOAD_EXIT_CODE = "__CALSCI_SIMULATOR_RELOAD__"

PRINTABLE_SHORTCUTS = {
    "0": "0",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    ".": ".",
    ",": ",",
    "(": "(",
    ")": ")",
    "+": "+",
    "-": "-",
    "/": "/",
    "*": "*",
}

KEYCODE_SHORTCUTS = {
    pygame.K_RETURN: "ok",
    pygame.K_BACKSPACE: "back",
    pygame.K_DELETE: "nav_b",
    pygame.K_ESCAPE: "home",
    pygame.K_UP: "nav_u",
    pygame.K_DOWN: "nav_d",
    pygame.K_LEFT: "nav_l",
    pygame.K_RIGHT: "nav_r",
    pygame.K_F1: "F1",
    pygame.K_F2: "F2",
    pygame.K_F3: "F3",
    pygame.K_F4: "F4",
    pygame.K_F6: "F6",
}

CTRL_SHORTCUTS = {
    pygame.K_a: "alpha",
    pygame.K_b: "beta",
    pygame.K_h: "home",
    pygame.K_l: "lock",
    pygame.K_LEFT: "back",
}


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


def _load_background_surface():
    if STATE.background_surface is not None:
        return STATE.background_surface

    for path in BACKGROUND_CANDIDATES:
        if path.exists():
            try:
                STATE.background_surface = pygame.image.load(str(path)).convert()
                break
            except Exception:
                STATE.background_surface = None

    return STATE.background_surface


def _reference_rect(screen):
    width, height = screen.get_size()
    scale = min(width / REFERENCE_WIDTH, height / REFERENCE_HEIGHT)
    scaled_w = max(1, int(round(REFERENCE_WIDTH * scale)))
    scaled_h = max(1, int(round(REFERENCE_HEIGHT * scale)))
    x = (width - scaled_w) // 2
    y = (height - scaled_h) // 2
    return pygame.Rect(x, y, scaled_w, scaled_h)


def _scale_reference_rect(screen, rect):
    frame = _reference_rect(screen)
    scale_x = frame.width / REFERENCE_WIDTH
    scale_y = frame.height / REFERENCE_HEIGHT
    x, y, width, height = rect
    return pygame.Rect(
        frame.x + int(round(x * scale_x)),
        frame.y + int(round(y * scale_y)),
        max(1, int(round(width * scale_x))),
        max(1, int(round(height * scale_y))),
    )


def _get_scaled_background(screen):
    background = _load_background_surface()
    if background is None:
        return None, None

    target_rect = _reference_rect(screen)
    scale_key = (target_rect.width, target_rect.height)
    if STATE.background_scale_key != scale_key or STATE.background_scaled is None:
        STATE.background_scaled = pygame.transform.smoothscale(background, scale_key)
        STATE.background_scale_key = scale_key
        STATE.background_rect = target_rect

    return STATE.background_scaled, target_rect


def _display_pixel_on(x: int, y: int) -> bool:
    page = y >> 3
    bit = 1 << (y & 7)
    idx = page * LCD_WIDTH + x

    on = 1 if (STATE.framebuffer[idx] & bit) else 0
    if STATE.all_points_on:
        on = 1
    if STATE.invert:
        on = 0 if on else 1

    return bool(STATE.display_on and on)


def _build_display_svg() -> str:
    lines = [
        (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{LCD_WIDTH}" height="{LCD_HEIGHT}" '
            f'viewBox="0 0 {LCD_WIDTH} {LCD_HEIGHT}" '
            'shape-rendering="crispEdges">'
        ),
        '<g fill="#000000">',
    ]

    for y in range(LCD_HEIGHT):
        run_start = None
        for x in range(LCD_WIDTH):
            if _display_pixel_on(x, y):
                if run_start is None:
                    run_start = x
                continue

            if run_start is not None:
                lines.append(f'<rect x="{run_start}" y="{y}" width="{x - run_start}" height="1"/>')
                run_start = None

        if run_start is not None:
            lines.append(f'<rect x="{run_start}" y="{y}" width="{LCD_WIDTH - run_start}" height="1"/>')

    lines.append("</g>")
    lines.append("</svg>")
    return "\n".join(lines)


def save_display_screenshot() -> Path:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    stamp = time.strftime("%Y%m%d_%H%M%S")
    millis = int((time.time() % 1.0) * 1000)
    filename = f"display_{stamp}_{millis:03d}.svg"
    output_path = SCREENSHOT_DIR / filename
    output_path.write_text(_build_display_svg(), encoding="utf-8")
    return output_path


def get_scale(screen):
    frame = _reference_rect(screen)
    if frame.width <= 0 or frame.height <= 0:
        return 1.0
    return min(frame.width / REFERENCE_WIDTH, frame.height / REFERENCE_HEIGHT)


def scale_value(value, screen, min_value=0):
    scaled = int(round(value * get_scale(screen)))
    return max(min_value, scaled)


def _display_metrics(screen):
    if _load_background_surface() is not None:
        rect = _scale_reference_rect(screen, REFERENCE_DISPLAY_RECT)
        return 1, 0, rect.width, rect.height

    box = scale_value(BASE_PIXEL_SIZE, screen, min_value=1)
    gap = scale_value(BASE_PIXEL_GAP, screen, min_value=0)
    display_w = LCD_WIDTH * (box + gap)
    display_h = LCD_HEIGHT * (box + gap)
    return box, gap, display_w, display_h


def _display_rect(screen):
    if _load_background_surface() is not None:
        return _scale_reference_rect(screen, REFERENCE_DISPLAY_RECT)

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
    scaled_background, target_rect = _get_scaled_background(screen)
    if scaled_background is not None:
        screen.fill((0, 0, 0))
        screen.blit(scaled_background, target_rect)
        return

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

    def draw(self, screen, pressed=False, amount=1.0):
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

    def draw(self, screen, pressed=False, amount=1.0):
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


class HotspotButton:
    def __init__(self, rect, shape="rect"):
        self.rect = rect
        self.shape = shape

    def draw(self, screen, pressed=False, amount=1.0):
        if not pressed or amount <= 0.0:
            return

        draw_rect = self.rect
        travel = max(1, int(round(min(draw_rect.width, draw_rect.height) * 0.08 * amount)))
        pressed_rect = draw_rect.move(0, travel)

        # Fade the original raised key a bit so the shifted pressed key reads clearly.
        wash = pygame.Surface(draw_rect.size, pygame.SRCALPHA)
        wash_alpha = int(round(52 * amount))
        if self.shape == "circle":
            pygame.draw.ellipse(wash, (*KEY_WELL_BG, wash_alpha), wash.get_rect())
        else:
            wash_radius = max(8, min(18, min(draw_rect.width, draw_rect.height) // 4))
            pygame.draw.rect(wash, (*KEY_WELL_BG, wash_alpha), wash.get_rect(), border_radius=wash_radius)
        screen.blit(wash, draw_rect)

        # Reduce the lower shadow from the original JPEG so the key looks less lifted.
        cover_h = max(2, int(round(draw_rect.height * 0.14 * amount)))
        cover_rect = pygame.Rect(draw_rect.x, draw_rect.bottom - cover_h, draw_rect.width, cover_h + travel)
        cover = pygame.Surface(cover_rect.size, pygame.SRCALPHA)
        cover_alpha = int(round(120 * amount))
        if self.shape == "circle":
            pygame.draw.ellipse(cover, (*KEY_WELL_BG, cover_alpha), cover.get_rect())
        else:
            cover_radius = max(8, min(18, min(cover_rect.width, cover_rect.height) // 4))
            pygame.draw.rect(cover, (*KEY_WELL_BG, cover_alpha), cover.get_rect(), border_radius=cover_radius)
        screen.blit(cover, cover_rect)

        overlay = pygame.Surface(pressed_rect.size, pygame.SRCALPHA)
        fill = (*KEY_PRESS_FILL, int(round(178 * amount)))
        stroke = (*KEY_PRESS_BORDER, int(round(168 * amount)))
        hilt = (*KEY_PRESS_HILITE, int(round(88 * amount)))
        shade = (*KEY_PRESS_SHADE, int(round(94 * amount)))

        if self.shape == "circle":
            pygame.draw.ellipse(overlay, fill, overlay.get_rect())
            pygame.draw.ellipse(overlay, stroke, overlay.get_rect(), width=2)

            top_arc = overlay.get_rect().inflate(-max(6, overlay.get_width() // 6), -max(10, overlay.get_height() // 3))
            top_arc.height = max(4, overlay.get_height() // 3)
            pygame.draw.ellipse(overlay, hilt, top_arc, width=2)

            bottom_arc = overlay.get_rect().inflate(-max(8, overlay.get_width() // 5), -max(10, overlay.get_height() // 3))
            bottom_arc.height = max(4, overlay.get_height() // 3)
            bottom_arc.top = overlay.get_height() - bottom_arc.height - 3
            pygame.draw.ellipse(overlay, shade, bottom_arc, width=2)
        else:
            radius = max(8, min(18, min(pressed_rect.width, pressed_rect.height) // 4))
            pygame.draw.rect(overlay, fill, overlay.get_rect(), border_radius=radius)
            pygame.draw.rect(overlay, stroke, overlay.get_rect(), width=2, border_radius=radius)

            inner_left = max(6, int(round(pressed_rect.width * 0.12)))
            inner_right = pressed_rect.width - inner_left
            top_y = max(3, int(round(pressed_rect.height * 0.18)))
            bottom_y = pressed_rect.height - max(4, int(round(pressed_rect.height * 0.16)))
            pygame.draw.line(overlay, hilt, (inner_left, top_y), (inner_right, top_y), width=2)
            pygame.draw.line(overlay, shade, (inner_left, bottom_y), (inner_right, bottom_y), width=2)

        screen.blit(overlay, pressed_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


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


def _build_image_key_widgets(screen):
    widgets = []
    for widget_id, (key, rect, shape) in enumerate(IMAGE_BUTTON_LAYOUT):
        mapped_row = None
        mapped_col = None
        coord = KEY_TO_COORD.get(key)
        if coord is not None:
            mapped_row, mapped_col = coord

        button = HotspotButton(_scale_reference_rect(screen, rect), shape=shape)
        widgets.append(_KeyWidget(button, widget_id, mapped_row, mapped_col))

    return widgets


def _build_key_widgets(screen):
    if _load_background_surface() is not None:
        return _build_image_key_widgets(screen)

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
        ["home", "settings", "back"],
        ["alpha", "beta", "lock"],
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
        ["toolbox", "pi", "log", "sin", "cos", "tan"],
        ["fraction", "pow", "root", ",", "(", ")"],
        ["F1", "F2", "F3", "F4", "F5", "F6"],
    ]

    section_2_layouts = [
        ["7", "8", "9", "nav_b", "AC"],
        ["4", "5", "6", "*", "/"],
        ["1", "2", "3", "+", "-"],
        [".", "0", "*pow(10, )", "ans", "exe"],
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
    STATE.lcd_surface = pygame.Surface((LCD_WIDTH, LCD_HEIGHT), pygame.SRCALPHA)

    _ensure_fonts(get_scale(STATE.screen))
    STATE.key_widgets = _build_key_widgets(STATE.screen)

    STATE.initialized = True
    render(force=True)


def shutdown_ui():
    if not pygame.get_init():
        return
    pygame.quit()


def _queue_key(row_idx: int, col_idx: int, widget_id: Optional[int] = None):
    _play_click()
    STATE.pending_keys.append((row_idx, col_idx))
    STATE.last_widget_id = widget_id
    STATE.last_key_ts = time.monotonic()


def _coord_for_key(key: str):
    coord = KEY_TO_COORD.get(key)
    if coord is None:
        return None
    row, col = coord
    return (row, col)


def _widget_id_for_coord(row_idx: int, col_idx: int) -> Optional[int]:
    for item in STATE.key_widgets:
        if item.row == row_idx and item.col == col_idx:
            return item.widget_id
    return None


def _queue_key_by_name(key_name: str) -> bool:
    coord = _coord_for_key(key_name)
    if coord is None:
        return False

    row_idx, col_idx = coord
    _queue_key(row_idx, col_idx, widget_id=_widget_id_for_coord(row_idx, col_idx))
    return True


def _keydown_action(event):
    ctrl_held = bool(event.mod & pygame.KMOD_CTRL)

    if event.key == pygame.K_F5:
        return ("reload", None)

    if ctrl_held and event.key == pygame.K_q:
        return ("quit", None)

    if ctrl_held:
        key_name = CTRL_SHORTCUTS.get(event.key)
        if key_name is not None:
            return ("queue", key_name)
        return (None, None)

    if event.key == pygame.K_s:
        return ("screenshot", None)

    key_name = KEYCODE_SHORTCUTS.get(event.key)
    if key_name is not None:
        return ("queue", key_name)

    key_name = PRINTABLE_SHORTCUTS.get(event.unicode)
    if key_name is not None:
        return ("queue", key_name)

    return (None, None)


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
            action, payload = _keydown_action(event)

            if action == "quit":
                raise SystemExit(0)
            if action == "reload":
                raise SystemExit(RELOAD_EXIT_CODE)
            if action == "screenshot":
                try:
                    output_path = save_display_screenshot()
                except OSError as exc:
                    print(f"[sim_ui] screenshot failed: {exc}")
                else:
                    print(f"[sim_ui] screenshot saved: {output_path}")
                continue
            if action == "queue" and payload is not None:
                _queue_key_by_name(payload)

    if STATE.dirty or (time.monotonic() - STATE.last_key_ts) < PRESS_TOTAL_SECS:
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


def pop_pending_keys():
    poll_events()
    items = list(STATE.pending_keys)
    STATE.pending_keys.clear()
    return items


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
    background_mode = _load_background_surface() is not None
    off_color = LCD_OFF_BACKGROUND if background_mode else LCD_OFF
    STATE.lcd_surface.fill((*off_color, 255))

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
                if STATE.display_on and on:
                    color = (*LCD_ON, 255)
                else:
                    color = (*off_color, 255)
                STATE.lcd_surface.set_at((x, y_base + bit), color)


def _press_amount(now: float, last_key_ts: float) -> float:
    elapsed = now - last_key_ts
    if elapsed < 0 or elapsed >= PRESS_TOTAL_SECS:
        return 0.0
    if elapsed <= PRESS_HOLD_SECS:
        return 1.0

    t = (elapsed - PRESS_HOLD_SECS) / PRESS_RELEASE_SECS
    t = max(0.0, min(1.0, t))
    # Smoothly ease the key back to its raised position.
    return 1.0 - (t * t * (3.0 - 2.0 * t))


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
        amount = _press_amount(now, STATE.last_key_ts) if STATE.last_widget_id == item.widget_id else 0.0
        item.widget.draw(STATE.screen, pressed=amount > 0.0, amount=amount)

    pygame.display.flip()
    STATE.last_render = now
    STATE.dirty = False
