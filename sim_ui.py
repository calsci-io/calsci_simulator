from __future__ import annotations

from array import array
import math
import subprocess
import threading
import time
from collections import deque
from pathlib import Path
from typing import Optional

import pygame
try:
    from PIL import Image, ImageSequence
except Exception:
    Image = None
    ImageSequence = None

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
EXPORT_TEMPLATE_CANDIDATES = [
    Path(__file__).resolve().parent / "assets" / "calsci_hero_app.png",
    Path("/home/sobik/Downloads/calsci_hero_app.png"),
]
SCREENSHOT_DIR = Path(__file__).resolve().parent.parent / "simulator_screen_shots"
VIDEO_DIR = Path(__file__).resolve().parent.parent / "simulator_videos"
VIDEO_FILENAME_PREFIX = "display"
VIDEO_FPS = 20
VIDEO_SCALE = 6
EXPORT_FRAME_MAX_DIM = 1080
GIF_FALLBACK_MAX_COLORS = 255
CLICK_SAMPLE_RATE = 22050
CLICK_VOLUME = 0.22
CLICK_DURATION_SECONDS = 0.035

SCREENSHOT_MODE_SVG = "svg"
SCREENSHOT_MODE_DISPLAY = "display"
SCREENSHOT_MODE_SIMULATOR = "simulator"

VIDEO_MODE_DISPLAY = "display"
VIDEO_MODE_SIMULATOR = "simulator"
VIDEO_MODE_APNG = "apng"
VIDEO_MODE_WEBM = "webm"
VIDEO_MODE_GIF = "gif"

MENU_TAB_SCREENSHOT = "screenshot"
MENU_TAB_VIDEO = "video"

SCREENSHOT_MODE_OPTIONS = (
    (SCREENSHOT_MODE_SVG, "SVG Pixels"),
    (SCREENSHOT_MODE_DISPLAY, "Display Background"),
    (SCREENSHOT_MODE_SIMULATOR, "Simulator Screenshot"),
)

VIDEO_MODE_OPTIONS = (
    (VIDEO_MODE_SIMULATOR, "Simulator Video"),
    (VIDEO_MODE_DISPLAY, "Display Background"),
    (VIDEO_MODE_APNG, "Transparent APNG"),
    (VIDEO_MODE_WEBM, "Transparent WebM"),
    (VIDEO_MODE_GIF, "Transparent GIF"),
)

SCREENSHOT_FILENAME_PREFIX = {
    SCREENSHOT_MODE_SVG: "display_svg",
    SCREENSHOT_MODE_DISPLAY: "display_background",
    SCREENSHOT_MODE_SIMULATOR: "simulator",
}

VIDEO_FILENAME_PREFIX = {
    VIDEO_MODE_SIMULATOR: "simulator",
    VIDEO_MODE_DISPLAY: "display_background",
    VIDEO_MODE_APNG: "simulator_transparent",
    VIDEO_MODE_WEBM: "simulator_transparent",
    VIDEO_MODE_GIF: "simulator_transparent",
}

VIDEO_FILENAME_SUFFIX = {
    VIDEO_MODE_SIMULATOR: "mp4",
    VIDEO_MODE_DISPLAY: "mp4",
    VIDEO_MODE_APNG: "apng",
    VIDEO_MODE_WEBM: "webm",
    VIDEO_MODE_GIF: "gif",
}

MENU_BG = (246, 246, 246)
MENU_BORDER = (72, 72, 72)
MENU_SHADOW = (30, 30, 30, 50)
MENU_TEXT = (22, 22, 22)
MENU_MUTED = (92, 92, 92)
MENU_TAB_ACTIVE = (227, 227, 227)
MENU_TAB_INACTIVE = (212, 212, 212)
MENU_BUTTON_BG = (236, 236, 236)
MENU_BUTTON_ACTIVE = (217, 227, 241)
MENU_ACTION_BG = (35, 35, 35)
MENU_ACTION_TEXT = (255, 255, 255)
MENU_FIELD_BG = (255, 255, 255)
MENU_FIELD_ACTIVE = (225, 236, 252)
MENU_ACCENT = (40, 111, 188)
MENU_WHITE = (255, 255, 255)
VIDEO_LIMIT_FIELD_ID = "video_limit"
VIDEO_LIMIT_MAX_CHARS = 8

# Active LCD plane measured from the inner sharp-edged screen cutout
# in the reference mockup, not the rounded outer display bezel.
REFERENCE_DISPLAY_RECT = (191, 150, 508, 264)
EXPORT_TEMPLATE_DISPLAY_RECT_FRAC = (
    0.140278,
    0.204167,
    0.705556,
    0.366667,
)

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
        self.export_template_surface = None
        self.export_template_scale_key = None
        self.export_template_scaled = None
        self.export_display_rect = None
        self.export_display_bg_scaled = None
        self.export_display_bg_scale_key = None

        self.main_font = None
        self.label_font = None
        self.tiny_label_font = None
        self.menu_font = None
        self.menu_label_font = None
        self.menu_help_font = None
        self.fallback_font = None
        self.emoji_font = None
        self._last_scale = None

        self.key_widgets = []
        self.pending_keys = deque()
        self.active_sources = {}
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
        self.recording_process = None
        self.recording_path = None
        self.recording_process_path = None
        self.recording_last_frame = None
        self.recording_next_frame_at = 0.0
        self.recording_thread = None
        self.recording_stop_event = None
        self.recording_frame_lock = threading.Lock()
        self.recording_error = None
        self.recording_frame_dirty = True
        self.recording_mode = VIDEO_MODE_SIMULATOR
        self.recording_deadline_at = None
        self.recording_started_at = None

        self.menu_open = False
        self.menu_tab = MENU_TAB_SCREENSHOT
        self.menu_focus_field = None
        self.screenshot_mode = SCREENSHOT_MODE_SIMULATOR
        self.video_mode = VIDEO_MODE_SIMULATOR
        self.video_limit_input = ""


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
            pygame.mixer.init(
                frequency=CLICK_SAMPLE_RATE,
                size=-16,
                channels=1,
                buffer=256,
            )

        sample_count = max(1, int(CLICK_SAMPLE_RATE * CLICK_DURATION_SECONDS))
        pcm = array("h")
        for idx in range(sample_count):
            t = idx / CLICK_SAMPLE_RATE
            progress = idx / max(1, sample_count - 1)
            attack = 1.0 - progress

            # A tactile "click" is mostly a sharp transient plus a tiny body.
            primary = math.sin(2.0 * math.pi * 2350.0 * t) * math.exp(-t * 95.0)
            body = math.sin(2.0 * math.pi * 780.0 * t) * math.exp(-t * 42.0)
            rebound = math.sin(2.0 * math.pi * 1680.0 * max(0.0, t - 0.009)) * math.exp(-max(0.0, t - 0.009) * 150.0)

            amplitude = (primary * 0.9) + (body * 0.45) + (rebound * 0.35)
            pcm.append(int(max(-1.0, min(1.0, amplitude * attack)) * 32767 * CLICK_VOLUME))

        STATE.click_sound = pygame.mixer.Sound(buffer=pcm.tobytes())
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


def _load_export_template_surface():
    if STATE.export_template_surface is not None:
        return STATE.export_template_surface

    for path in EXPORT_TEMPLATE_CANDIDATES:
        if path.exists():
            try:
                STATE.export_template_surface = pygame.image.load(str(path)).convert_alpha()
                break
            except Exception:
                STATE.export_template_surface = None

    return STATE.export_template_surface


def _export_template_display_rect_for(surface):
    return _scale_export_display_rect(surface.get_size())


def _scale_export_display_rect(size):
    width, height = size
    x_frac, y_frac, w_frac, h_frac = EXPORT_TEMPLATE_DISPLAY_RECT_FRAC
    x = int(round(width * x_frac))
    y = int(round(height * y_frac))
    w = max(1, int(round(width * w_frac)))
    h = max(1, int(round(height * h_frac)))
    if x + w > width:
        w = max(1, width - x)
    if y + h > height:
        h = max(1, height - y)
    return pygame.Rect(x, y, w, h)


def _get_scaled_export_template():
    template = _load_export_template_surface()
    if template is None:
        return None, None

    template_w, template_h = template.get_size()
    scale = min(
        1.0,
        EXPORT_FRAME_MAX_DIM / max(1, template_w),
        EXPORT_FRAME_MAX_DIM / max(1, template_h),
    )
    target_size = (
        max(1, int(round(template_w * scale))),
        max(1, int(round(template_h * scale))),
    )

    if (
        STATE.export_template_scaled is None
        or STATE.export_template_scale_key != target_size
    ):
        if target_size == (template_w, template_h):
            STATE.export_template_scaled = template.copy()
        else:
            STATE.export_template_scaled = pygame.transform.smoothscale(template, target_size)
        STATE.export_template_scale_key = target_size
        STATE.export_display_rect = _scale_export_display_rect(target_size)

    return STATE.export_template_scaled, STATE.export_display_rect


def _get_scaled_export_display_background(size):
    template = _load_export_template_surface()
    if template is None:
        return None

    target_size = (max(1, int(size[0])), max(1, int(size[1])))
    if (
        STATE.export_display_bg_scaled is not None
        and STATE.export_display_bg_scale_key == target_size
    ):
        return STATE.export_display_bg_scaled

    crop_rect = _export_template_display_rect_for(template)
    display_crop = template.subsurface(crop_rect).copy()
    if display_crop.get_size() == target_size:
        STATE.export_display_bg_scaled = display_crop
    else:
        STATE.export_display_bg_scaled = pygame.transform.smoothscale(display_crop, target_size)
    STATE.export_display_bg_scale_key = target_size
    return STATE.export_display_bg_scaled


def _display_capture_size():
    _template_surface, display_rect = _get_scaled_export_template()
    if display_rect is not None:
        return display_rect.size
    return (LCD_WIDTH * VIDEO_SCALE, LCD_HEIGHT * VIDEO_SCALE)


def _build_display_background_surface(size):
    background = _get_scaled_export_display_background(size)
    if background is not None:
        return background.copy()

    surface = pygame.Surface(size)
    surface.fill(LCD_OFF_BACKGROUND)
    return surface


def _build_display_export_surface():
    if STATE.lcd_surface is None:
        return None

    target_size = _display_capture_size()
    export_surface = _build_display_background_surface(target_size)
    scaled_lcd = pygame.transform.scale(STATE.lcd_surface, target_size)
    export_surface.blit(scaled_lcd, (0, 0))
    return export_surface


def _build_simulator_export_surface(white_background=False):
    template_surface, display_rect = _get_scaled_export_template()
    if template_surface is None or display_rect is None or STATE.lcd_surface is None:
        return _build_display_export_surface()

    if white_background:
        export_surface = pygame.Surface(template_surface.get_size())
        export_surface.fill(MENU_WHITE)
    else:
        export_surface = pygame.Surface(template_surface.get_size(), pygame.SRCALPHA)
        export_surface.fill((0, 0, 0, 0))
    export_surface.blit(template_surface, (0, 0))
    scaled_lcd = pygame.transform.scale(
        STATE.lcd_surface,
        (display_rect.width, display_rect.height),
    )
    export_surface.blit(scaled_lcd, display_rect.topleft)
    return export_surface


def _build_capture_surface(mode, for_video=False):
    if mode == SCREENSHOT_MODE_DISPLAY or mode == VIDEO_MODE_DISPLAY:
        return _build_display_export_surface()
    if mode in (VIDEO_MODE_APNG, VIDEO_MODE_WEBM, VIDEO_MODE_GIF):
        return _build_simulator_export_surface(white_background=False)
    if mode == SCREENSHOT_MODE_SIMULATOR or mode == VIDEO_MODE_SIMULATOR:
        return _build_simulator_export_surface(white_background=for_video)
    return None


def _capture_recording_frame(mode=None):
    _draw_lcd_pixels()
    selected_mode = mode or STATE.recording_mode or STATE.video_mode
    export_surface = _build_capture_surface(selected_mode, for_video=True)
    if export_surface is not None:
        if selected_mode in (VIDEO_MODE_APNG, VIDEO_MODE_WEBM, VIDEO_MODE_GIF):
            return pygame.image.tobytes(export_surface, "RGBA"), export_surface.get_size(), "rgba"
        return pygame.image.tobytes(export_surface, "RGB"), export_surface.get_size(), "rgb24"
    return pygame.image.tobytes(STATE.lcd_surface, "RGB"), (LCD_WIDTH, LCD_HEIGHT), "rgb24"


def save_display_screenshot(mode=None) -> Path:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    stamp = time.strftime("%Y%m%d_%H%M%S")
    millis = int((time.time() % 1.0) * 1000)
    ensure_ui()
    _draw_lcd_pixels()

    selected_mode = mode or STATE.screenshot_mode
    if selected_mode == SCREENSHOT_MODE_SVG:
        filename = f"{SCREENSHOT_FILENAME_PREFIX[selected_mode]}_{stamp}_{millis:03d}.svg"
        output_path = SCREENSHOT_DIR / filename
        output_path.write_text(_build_display_svg(), encoding="utf-8")
        return output_path

    export_surface = _build_capture_surface(selected_mode, for_video=False)
    if export_surface is not None:
        filename = f"{SCREENSHOT_FILENAME_PREFIX[selected_mode]}_{stamp}_{millis:03d}.png"
        output_path = SCREENSHOT_DIR / filename
        pygame.image.save(export_surface, str(output_path))
        return output_path

    filename = f"{SCREENSHOT_FILENAME_PREFIX[SCREENSHOT_MODE_SVG]}_{stamp}_{millis:03d}.svg"
    output_path = SCREENSHOT_DIR / filename
    output_path.write_text(_build_display_svg(), encoding="utf-8")
    return output_path


def _build_timestamped_output_path(directory: Path, prefix: str, suffix: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)

    stamp = time.strftime("%Y%m%d_%H%M%S")
    millis = int((time.time() % 1.0) * 1000)
    filename = f"{prefix}_{stamp}_{millis:03d}.{suffix}"
    return directory / filename


def _build_gif_intermediate_path(final_path: Path) -> Path:
    return final_path.with_name(final_path.stem + "__recording.apng")


def _recording_active() -> bool:
    return STATE.recording_process is not None


def _capture_display_frame_bytes() -> bytes:
    frame_bytes, _, _ = _capture_recording_frame()
    return frame_bytes


def _mark_lcd_dirty():
    STATE.dirty = True
    STATE.recording_frame_dirty = True


def _clear_recording_state():
    stop_event = STATE.recording_stop_event
    if stop_event is not None:
        stop_event.set()

    STATE.recording_process = None
    STATE.recording_path = None
    STATE.recording_process_path = None
    STATE.recording_last_frame = None
    STATE.recording_next_frame_at = 0.0
    STATE.recording_thread = None
    STATE.recording_stop_event = None
    STATE.recording_error = None
    STATE.recording_frame_dirty = True
    STATE.recording_mode = STATE.video_mode
    STATE.recording_deadline_at = None
    STATE.recording_started_at = None
    STATE.dirty = True


def _close_recording_process(process: subprocess.Popen[bytes], timeout: float = 10.0):
    stderr_text = ""

    if process.stdin is not None and not process.stdin.closed:
        process.stdin.close()

    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()

    if process.stderr is not None:
        try:
            stderr_data = process.stderr.read()
        finally:
            process.stderr.close()
        if stderr_data:
            stderr_text = stderr_data.decode("utf-8", errors="replace").strip()

    return process.returncode, stderr_text


def _join_recording_thread(timeout: float = 2.0):
    thread = STATE.recording_thread
    if thread is None or thread is threading.current_thread():
        return
    if thread.is_alive():
        thread.join(timeout=timeout)


def _abort_display_recording(detail: str) -> str:
    process = STATE.recording_process
    output_path = STATE.recording_path
    process_output_path = STATE.recording_process_path
    stop_event = STATE.recording_stop_event
    if stop_event is not None:
        stop_event.set()
    _join_recording_thread(timeout=1.0)
    _clear_recording_state()

    stderr_text = ""
    if process is not None:
        _, stderr_text = _close_recording_process(process, timeout=3.0)

    message = detail
    if stderr_text:
        message = f"{detail}: {stderr_text}" if detail else stderr_text

    for path in (process_output_path, output_path):
        if path is None:
            continue
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        except Exception:
            pass

    if output_path is not None:
        print(f"[sim_ui] recording failed for {output_path}: {message}")
    else:
        print(f"[sim_ui] recording failed: {message}")
    return message


def _write_recording_frame(frame_bytes: bytes) -> Optional[str]:
    process = STATE.recording_process
    if process is None or process.stdin is None:
        return "recording process is not available"

    try:
        process.stdin.write(frame_bytes)
    except (BrokenPipeError, OSError) as exc:
        return _abort_display_recording(str(exc))

    return None


def _refresh_recording_frame_cache():
    frame_bytes = _capture_display_frame_bytes()
    with STATE.recording_frame_lock:
        STATE.recording_last_frame = frame_bytes
        STATE.recording_frame_dirty = False


def _recording_writer_loop(process: subprocess.Popen[bytes], stop_event: threading.Event):
    frame_interval = 1.0 / VIDEO_FPS
    next_frame_at = time.monotonic()

    while not stop_event.is_set():
        with STATE.recording_frame_lock:
            frame_bytes = STATE.recording_last_frame

        if frame_bytes is not None:
            try:
                process.stdin.write(frame_bytes)
            except (BrokenPipeError, OSError) as exc:
                STATE.recording_error = str(exc)
                stop_event.set()
                return

        next_frame_at += frame_interval
        delay = next_frame_at - time.monotonic()
        if delay > 0:
            stop_event.wait(delay)
        else:
            next_frame_at = time.monotonic()


def _pump_video_recording(now: Optional[float] = None) -> Optional[str]:
    current_time = time.monotonic() if now is None else now

    if not _recording_active():
        return None

    if STATE.recording_error is not None:
        error = STATE.recording_error
        STATE.recording_error = None
        return _abort_display_recording(error)

    deadline = STATE.recording_deadline_at
    if deadline is not None and current_time >= deadline:
        try:
            output_path = stop_display_recording()
        except OSError as exc:
            print(f"[sim_ui] recording failed: {exc}")
        else:
            print(f"[sim_ui] recording saved: {output_path}")

    return None


def _extend_webm_recording_command(command, output_path: Path, crf="30", cpu_used="4"):
    command.extend(
        [
            "-c:v",
            "libvpx-vp9",
            "-pix_fmt",
            "yuva420p",
            "-metadata:s:v:0",
            "alpha_mode=1",
            "-b:v",
            "0",
            "-crf",
            str(crf),
            "-deadline",
            "realtime",
            "-cpu-used",
            str(cpu_used),
            "-row-mt",
            "1",
            "-auto-alt-ref",
            "0",
            str(output_path),
        ]
    )


def _extend_gif_intermediate_recording_command(command, output_path: Path):
    command.extend(
        [
            "-c:v",
            "apng",
            "-pix_fmt",
            "rgba",
            "-plays",
            "0",
            str(output_path),
        ]
    )


def _optimize_gif_recording_with_ffmpeg(source_path: Path, target_path: Path, duration_seconds=None):
    temp_output_path = target_path.with_name(target_path.stem + "__optimized.gif")

    filter_complex = (
        "[0:v]split[palette_in][gif_in];"
        f"[palette_in]palettegen=max_colors={GIF_FALLBACK_MAX_COLORS}:"
        "reserve_transparent=1:stats_mode=diff[palette];"
        "[gif_in][palette]paletteuse=alpha_threshold=128:"
        "dither=bayer:bayer_scale=3:diff_mode=rectangle"
    )

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(source_path),
                "-filter_complex",
                filter_complex,
                "-gifflags",
                "+transdiff",
                "-loop",
                "0",
                str(temp_output_path),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        stderr_text = ""
        try:
            stderr_text = (exc.stderr or b"").decode("utf-8", errors="replace").strip()
        except Exception:
            stderr_text = ""
        detail = stderr_text or "ffmpeg gif optimization failed"
        raise OSError(detail) from exc

    temp_output_path.replace(target_path)
    try:
        source_path.unlink()
    except FileNotFoundError:
        pass
    except Exception:
        pass


def _optimize_gif_recording_with_pillow(source_path: Path, target_path: Path, duration_seconds=None):
    if Image is None or ImageSequence is None:
        raise RuntimeError("Pillow is not available")

    source_image = Image.open(source_path)
    frames = []
    durations = []
    previous_rgba = None
    previous_bytes = None
    accumulated_ms = 0
    default_frame_ms = int(round(1000.0 / max(1, VIDEO_FPS)))

    for frame in ImageSequence.Iterator(source_image):
        rgba = frame.convert("RGBA")
        frame_ms = frame.info.get("duration", default_frame_ms)
        try:
            frame_ms = int(round(float(frame_ms)))
        except Exception:
            frame_ms = default_frame_ms
        frame_ms = max(20, frame_ms)

        frame_bytes = rgba.tobytes()
        if previous_bytes is not None and frame_bytes == previous_bytes:
            accumulated_ms += frame_ms
            continue

        if previous_rgba is not None:
            frames.append(previous_rgba)
            durations.append(accumulated_ms)

        previous_rgba = rgba.copy()
        previous_bytes = frame_bytes
        accumulated_ms = frame_ms

    if previous_rgba is not None:
        frames.append(previous_rgba)
        durations.append(accumulated_ms)

    if not frames:
        raise OSError("gif optimizer found no frames")

    target_total_ms = None
    if duration_seconds is not None:
        try:
            target_total_ms = int(round(float(duration_seconds) * 1000.0))
        except Exception:
            target_total_ms = None
    if target_total_ms is None or target_total_ms <= 0:
        target_total_ms = sum(durations)

    current_total_ms = sum(durations)
    delta_ms = target_total_ms - current_total_ms
    durations[-1] = max(20, durations[-1] + delta_ms)

    temp_output_path = target_path.with_name(target_path.stem + "__optimized.gif")
    frames[0].save(
        temp_output_path,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=durations,
        optimize=True,
        disposal=2,
    )
    temp_output_path.replace(target_path)

    try:
        source_image.close()
    except Exception:
        pass
    try:
        source_path.unlink()
    except FileNotFoundError:
        pass
    except Exception:
        pass


def _optimize_gif_recording(source_path: Path, target_path: Path, duration_seconds=None):
    try:
        _optimize_gif_recording_with_pillow(
            source_path,
            target_path,
            duration_seconds=duration_seconds,
        )
        return
    except Exception:
        pass

    _optimize_gif_recording_with_ffmpeg(
        source_path,
        target_path,
        duration_seconds=duration_seconds,
    )


def start_display_recording(mode=None, limit_seconds=None) -> Path:
    ensure_ui()

    if _recording_active() and STATE.recording_path is not None:
        return STATE.recording_path

    selected_mode = mode or STATE.video_mode
    output_path = _build_timestamped_output_path(
        VIDEO_DIR,
        VIDEO_FILENAME_PREFIX.get(selected_mode, "video"),
        VIDEO_FILENAME_SUFFIX.get(selected_mode, "mp4"),
    )
    process_output_path = output_path
    if selected_mode == VIDEO_MODE_GIF:
        process_output_path = _build_gif_intermediate_path(output_path)
    initial_frame, frame_size, input_pixel_format = _capture_recording_frame(mode=selected_mode)
    frame_width, frame_height = frame_size

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "rawvideo",
        "-pixel_format",
        input_pixel_format,
        "-video_size",
        f"{frame_width}x{frame_height}",
        "-framerate",
        str(VIDEO_FPS),
        "-i",
        "-",
    ]

    if selected_mode == VIDEO_MODE_APNG:
        command.extend(
            [
                "-c:v",
                "apng",
                "-pix_fmt",
                "rgba",
                "-plays",
                "0",
                str(output_path),
            ]
        )
    elif selected_mode == VIDEO_MODE_WEBM:
        _extend_webm_recording_command(command, output_path, crf="30", cpu_used="4")
    elif selected_mode == VIDEO_MODE_GIF:
        _extend_gif_intermediate_recording_command(command, process_output_path)
    else:
        video_filter = "format=yuv420p"
        if frame_size == (LCD_WIDTH, LCD_HEIGHT):
            video_filter = (
                f"scale={LCD_WIDTH * VIDEO_SCALE}:{LCD_HEIGHT * VIDEO_SCALE}:flags=neighbor,"
                "format=yuv420p"
            )
        command.extend(
            [
                "-vf",
                video_filter,
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-movflags",
                "+faststart",
                str(output_path),
            ]
        )

    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    except OSError as exc:
        raise OSError(f"unable to start ffmpeg: {exc}") from exc

    STATE.recording_process = process
    STATE.recording_path = output_path
    STATE.recording_process_path = process_output_path
    STATE.recording_mode = selected_mode
    STATE.recording_started_at = time.monotonic()
    with STATE.recording_frame_lock:
        STATE.recording_last_frame = initial_frame
        STATE.recording_frame_dirty = False
    STATE.recording_error = None
    STATE.recording_next_frame_at = time.monotonic() + (1.0 / VIDEO_FPS)
    if limit_seconds is not None and limit_seconds > 0:
        STATE.recording_deadline_at = time.monotonic() + float(limit_seconds)
    else:
        STATE.recording_deadline_at = None
    stop_event = threading.Event()
    STATE.recording_stop_event = stop_event
    STATE.recording_thread = threading.Thread(
        target=_recording_writer_loop,
        args=(process, stop_event),
        name="calsci-sim-recorder",
        daemon=True,
    )
    STATE.recording_thread.start()

    STATE.dirty = True
    return output_path


def stop_display_recording() -> Path:
    if not _recording_active() or STATE.recording_path is None:
        raise RuntimeError("display recording is not active")

    if STATE.recording_frame_dirty:
        _refresh_recording_frame_cache()

    process = STATE.recording_process
    output_path = STATE.recording_path
    process_output_path = STATE.recording_process_path
    recording_mode = STATE.recording_mode
    recording_started_at = STATE.recording_started_at
    stop_event = STATE.recording_stop_event
    if stop_event is not None:
        stop_event.set()
    _join_recording_thread(timeout=2.0)
    worker_error = STATE.recording_error
    _clear_recording_state()

    close_timeout = 30.0 if recording_mode == VIDEO_MODE_GIF else 10.0
    returncode, stderr_text = _close_recording_process(process, timeout=close_timeout)
    if returncode != 0:
        detail = stderr_text or f"ffmpeg exited with status {returncode}"
        raise OSError(detail)
    if worker_error:
        raise OSError(worker_error)

    if recording_mode == VIDEO_MODE_GIF:
        if process_output_path is None:
            raise OSError("gif recording output is missing")
        print(f"[sim_ui] optimizing gif locally: {output_path}")
        duration_seconds = None
        if recording_started_at is not None:
            duration_seconds = max(0.0, time.monotonic() - recording_started_at)
        _optimize_gif_recording(process_output_path, output_path, duration_seconds=duration_seconds)

    return output_path


def _stop_recording_for_exit():
    if not _recording_active():
        return

    try:
        output_path = stop_display_recording()
    except OSError as exc:
        print(f"[sim_ui] recording failed while closing: {exc}")
    else:
        print(f"[sim_ui] recording saved: {output_path}")


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
    menu_size = max(18, int(round(26 * scale)))
    menu_label_size = max(16, int(round(22 * scale)))
    menu_help_size = max(14, int(round(18 * scale)))

    STATE.main_font = _load_font("DejaVuSans.ttf", main_size)
    STATE.label_font = _load_font("DejaVuSans.ttf", label_size)
    STATE.tiny_label_font = _load_font("DejaVuSans.ttf", tiny_size)
    STATE.menu_font = _load_font("DejaVuSans.ttf", menu_size)
    STATE.menu_label_font = _load_font("DejaVuSans.ttf", menu_label_size)
    STATE.menu_help_font = _load_font("DejaVuSans.ttf", menu_help_size)
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


def _selected_video_limit_seconds():
    raw = str(STATE.video_limit_input or "").strip()
    if raw == "":
        return None
    try:
        value = float(raw)
    except ValueError:
        return None
    if not math.isfinite(value) or value <= 0:
        return None
    return value


def _draw_menu_text(screen, text, rect, color=MENU_TEXT, center=False, small=False, tiny=False):
    font = STATE.menu_help_font if tiny else STATE.menu_label_font if small else STATE.menu_font
    lines = str(text).splitlines() or [""]
    line_height = font.get_linesize()
    total_height = line_height * len(lines)
    start_y = rect.centery - (total_height // 2)

    for idx, line in enumerate(lines):
        rendered = font.render(line, True, color)
        if center:
            text_rect = rendered.get_rect(center=(rect.centerx, start_y + (idx * line_height) + (line_height // 2)))
        else:
            text_rect = rendered.get_rect(midleft=(rect.x, start_y + (idx * line_height) + (line_height // 2)))
        screen.blit(rendered, text_rect)


def _menu_layout(screen):
    scale = get_scale(screen)
    margin = max(14, int(round(20 * scale)))
    gap = max(8, int(round(12 * scale)))
    padding = max(14, int(round(18 * scale)))
    burger_w = max(54, int(round(66 * scale)))
    burger_h = max(42, int(round(52 * scale)))
    available_w = max(220, screen.get_width() - (margin * 2))
    panel_w = min(available_w, max(360, int(round(430 * scale))))
    tab_h = max(40, int(round(48 * scale)))
    option_h = max(42, int(round(50 * scale)))
    field_h = max(44, int(round(52 * scale)))
    action_h = max(46, int(round(54 * scale)))

    burger_rect = pygame.Rect(margin, margin, burger_w, burger_h)
    panel_rect = pygame.Rect(margin, burger_rect.bottom + gap, panel_w, 10)

    tabs_y = panel_rect.y + padding
    tab_w = (panel_w - (padding * 2) - gap) // 2
    tab_screenshot = pygame.Rect(panel_rect.x + padding, tabs_y, tab_w, tab_h)
    tab_video = pygame.Rect(tab_screenshot.right + gap, tabs_y, tab_w, tab_h)

    content_x = panel_rect.x + padding
    content_w = panel_w - (padding * 2)
    y = tab_screenshot.bottom + gap

    screenshot_rows = []
    for idx, (mode, _label) in enumerate(SCREENSHOT_MODE_OPTIONS):
        row_rect = pygame.Rect(content_x, y + idx * (option_h + gap), content_w, option_h)
        screenshot_rows.append((mode, row_rect))
    screenshot_button = pygame.Rect(
        content_x,
        screenshot_rows[-1][1].bottom + gap,
        content_w,
        action_h,
    )
    screenshot_help = pygame.Rect(
        content_x,
        screenshot_button.bottom + gap,
        content_w,
        max(34, int(round(44 * scale))),
    )
    screenshot_bottom = screenshot_help.bottom

    video_rows = []
    y_video = y
    for idx, (mode, _label) in enumerate(VIDEO_MODE_OPTIONS):
        row_rect = pygame.Rect(content_x, y_video + idx * (option_h + gap), content_w, option_h)
        video_rows.append((mode, row_rect))
    video_label = pygame.Rect(
        content_x,
        video_rows[-1][1].bottom + gap,
        content_w,
        max(24, int(round(28 * scale))),
    )
    video_field = pygame.Rect(content_x, video_label.bottom + gap, content_w, field_h)
    video_button = pygame.Rect(content_x, video_field.bottom + gap, content_w, action_h)
    video_help = pygame.Rect(
        content_x,
        video_button.bottom + gap,
        content_w,
        max(44, int(round(58 * scale))),
    )
    video_bottom = video_help.bottom

    panel_rect.height = (screenshot_bottom if STATE.menu_tab == MENU_TAB_SCREENSHOT else video_bottom) - panel_rect.y + padding

    return {
        "burger": burger_rect,
        "panel": panel_rect,
        "tab_screenshot": tab_screenshot,
        "tab_video": tab_video,
        "screenshot_rows": screenshot_rows,
        "screenshot_button": screenshot_button,
        "screenshot_help": screenshot_help,
        "video_rows": video_rows,
        "video_label": video_label,
        "video_field": video_field,
        "video_button": video_button,
        "video_help": video_help,
    }


def _draw_burger_button(screen, rect, open_state):
    fill = MENU_BUTTON_ACTIVE if open_state else MENU_BUTTON_BG
    pygame.draw.rect(screen, fill, rect, border_radius=10)
    pygame.draw.rect(screen, MENU_BORDER, rect, width=1, border_radius=10)

    line_margin_x = max(10, rect.width // 5)
    line_gap = max(5, rect.height // 6)
    line_y = rect.y + rect.height // 2 - line_gap
    for idx in range(3):
        start = (rect.x + line_margin_x, line_y + (idx * line_gap))
        end = (rect.right - line_margin_x, line_y + (idx * line_gap))
        pygame.draw.line(screen, MENU_TEXT, start, end, width=3)


def _draw_menu_option_row(screen, rect, label, selected):
    fill = MENU_BUTTON_ACTIVE if selected else MENU_BUTTON_BG
    pygame.draw.rect(screen, fill, rect, border_radius=10)
    pygame.draw.rect(screen, MENU_BORDER, rect, width=1, border_radius=10)

    radio_radius = max(9, min(12, rect.height // 4))
    radio_center = (rect.x + radio_radius + 16, rect.centery)
    pygame.draw.circle(screen, MENU_BORDER, radio_center, radio_radius, width=2)
    if selected:
        pygame.draw.circle(screen, MENU_ACCENT, radio_center, max(3, radio_radius - 4))

    text_rect = pygame.Rect(radio_center[0] + radio_radius + 14, rect.y, rect.width - 56, rect.height)
    _draw_menu_text(screen, label, text_rect, color=MENU_TEXT, small=False)


def _draw_menu_action_button(screen, rect, label, destructive=False):
    fill = (176, 40, 40) if destructive else MENU_ACTION_BG
    pygame.draw.rect(screen, fill, rect, border_radius=10)
    pygame.draw.rect(screen, MENU_BORDER, rect, width=1, border_radius=10)
    _draw_menu_text(screen, label, rect, color=MENU_ACTION_TEXT, center=True, small=False)


def _draw_menu_field(screen, rect, text_value, active=False):
    fill = MENU_FIELD_ACTIVE if active else MENU_FIELD_BG
    pygame.draw.rect(screen, fill, rect, border_radius=10)
    pygame.draw.rect(screen, MENU_ACCENT if active else MENU_BORDER, rect, width=2 if active else 1, border_radius=10)
    display_value = text_value if text_value else "blank = manual stop"
    display_color = MENU_TEXT if text_value else MENU_MUTED
    text_rect = pygame.Rect(rect.x + 14, rect.y, rect.width - 28, rect.height)
    _draw_menu_text(screen, display_value, text_rect, color=display_color, small=True)

    if active:
        font = STATE.menu_label_font
        rendered = font.render(display_value, True, display_color)
        caret_x = min(rect.right - 10, text_rect.x + rendered.get_width() + 2)
        caret_top = rect.y + 8
        caret_bottom = rect.bottom - 8
        pygame.draw.line(screen, MENU_ACCENT, (caret_x, caret_top), (caret_x, caret_bottom), width=2)


def _draw_capture_menu(screen):
    layout = _menu_layout(screen)
    _draw_burger_button(screen, layout["burger"], STATE.menu_open)
    if not STATE.menu_open:
        return

    shadow_rect = layout["panel"].move(4, 4)
    shadow = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 0))
    pygame.draw.rect(shadow, MENU_SHADOW, shadow.get_rect(), border_radius=14)
    screen.blit(shadow, shadow_rect.topleft)

    pygame.draw.rect(screen, MENU_BG, layout["panel"], border_radius=14)
    pygame.draw.rect(screen, MENU_BORDER, layout["panel"], width=1, border_radius=14)

    screenshot_fill = MENU_TAB_ACTIVE if STATE.menu_tab == MENU_TAB_SCREENSHOT else MENU_TAB_INACTIVE
    video_fill = MENU_TAB_ACTIVE if STATE.menu_tab == MENU_TAB_VIDEO else MENU_TAB_INACTIVE
    pygame.draw.rect(screen, screenshot_fill, layout["tab_screenshot"], border_radius=10)
    pygame.draw.rect(screen, video_fill, layout["tab_video"], border_radius=10)
    pygame.draw.rect(screen, MENU_BORDER, layout["tab_screenshot"], width=1, border_radius=10)
    pygame.draw.rect(screen, MENU_BORDER, layout["tab_video"], width=1, border_radius=10)
    _draw_menu_text(screen, "Screenshot", layout["tab_screenshot"], center=True, small=False)
    _draw_menu_text(screen, "Video", layout["tab_video"], center=True, small=False)

    if STATE.menu_tab == MENU_TAB_SCREENSHOT:
        for mode, rect in layout["screenshot_rows"]:
            label = dict(SCREENSHOT_MODE_OPTIONS).get(mode, mode)
            _draw_menu_option_row(screen, rect, label, mode == STATE.screenshot_mode)
        _draw_menu_action_button(screen, layout["screenshot_button"], "Save Screenshot")
        _draw_menu_text(
            screen,
            "SVG, display-only,\nor full simulator export.",
            layout["screenshot_help"],
            color=MENU_MUTED,
            tiny=True,
        )
    else:
        for mode, rect in layout["video_rows"]:
            label = dict(VIDEO_MODE_OPTIONS).get(mode, mode)
            _draw_menu_option_row(screen, rect, label, mode == STATE.video_mode)
        _draw_menu_text(
            screen,
            "Video Limit (seconds)",
            layout["video_label"],
            color=MENU_TEXT,
            small=False,
        )
        _draw_menu_field(
            screen,
            layout["video_field"],
            STATE.video_limit_input,
            active=STATE.menu_focus_field == VIDEO_LIMIT_FIELD_ID,
        )
        _draw_menu_action_button(
            screen,
            layout["video_button"],
            "Stop Recording" if _recording_active() else "Start Recording",
            destructive=_recording_active(),
        )
        _draw_menu_text(
            screen,
            "MP4, APNG, WebM, or GIF.\nPress V anytime to stop early.",
            layout["video_help"],
            color=MENU_MUTED,
            tiny=True,
        )


def _run_screenshot_action():
    try:
        output_path = save_display_screenshot(STATE.screenshot_mode)
    except OSError as exc:
        print(f"[sim_ui] screenshot failed: {exc}")
    else:
        print(f"[sim_ui] screenshot saved: {output_path}")
    STATE.dirty = True


def _toggle_recording_action():
    if _recording_active():
        try:
            output_path = stop_display_recording()
        except OSError as exc:
            print(f"[sim_ui] recording failed: {exc}")
        else:
            print(f"[sim_ui] recording saved: {output_path}")
    else:
        limit_seconds = _selected_video_limit_seconds()
        try:
            output_path = start_display_recording(
                mode=STATE.video_mode,
                limit_seconds=limit_seconds,
            )
        except OSError as exc:
            print(f"[sim_ui] recording failed: {exc}")
        else:
            if limit_seconds is None:
                print(f"[sim_ui] recording started: {output_path}")
            else:
                print(f"[sim_ui] recording started: {output_path} (limit {limit_seconds:g}s)")
    STATE.dirty = True


def _handle_menu_mouse_down(pos):
    layout = _menu_layout(STATE.screen)
    if layout["burger"].collidepoint(pos):
        STATE.menu_open = not STATE.menu_open
        if not STATE.menu_open:
            STATE.menu_focus_field = None
        STATE.dirty = True
        return True

    if not STATE.menu_open:
        return False

    if not layout["panel"].collidepoint(pos):
        STATE.menu_open = False
        STATE.menu_focus_field = None
        STATE.dirty = True
        return True

    if layout["tab_screenshot"].collidepoint(pos):
        STATE.menu_tab = MENU_TAB_SCREENSHOT
        STATE.menu_focus_field = None
        STATE.dirty = True
        return True
    if layout["tab_video"].collidepoint(pos):
        STATE.menu_tab = MENU_TAB_VIDEO
        STATE.dirty = True
        return True

    if STATE.menu_tab == MENU_TAB_SCREENSHOT:
        for mode, rect in layout["screenshot_rows"]:
            if rect.collidepoint(pos):
                STATE.screenshot_mode = mode
                STATE.dirty = True
                return True
        if layout["screenshot_button"].collidepoint(pos):
            _run_screenshot_action()
            return True
    else:
        for mode, rect in layout["video_rows"]:
            if rect.collidepoint(pos):
                STATE.video_mode = mode
                STATE.dirty = True
                return True
        if layout["video_field"].collidepoint(pos):
            STATE.menu_focus_field = VIDEO_LIMIT_FIELD_ID
            STATE.dirty = True
            return True
        STATE.menu_focus_field = None
        if layout["video_button"].collidepoint(pos):
            _toggle_recording_action()
            return True

    STATE.dirty = True
    return True


def _handle_menu_keydown(event):
    if not STATE.menu_open or STATE.menu_tab != MENU_TAB_VIDEO:
        return False
    if STATE.menu_focus_field != VIDEO_LIMIT_FIELD_ID:
        return False

    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        STATE.menu_focus_field = None
        STATE.dirty = True
        return True
    if event.key == pygame.K_BACKSPACE:
        STATE.video_limit_input = STATE.video_limit_input[:-1]
        STATE.dirty = True
        return True
    if event.key == pygame.K_DELETE:
        STATE.video_limit_input = ""
        STATE.dirty = True
        return True

    char = event.unicode
    if char and char in "0123456789.":
        if char == "." and "." in STATE.video_limit_input:
            return True
        if len(STATE.video_limit_input) >= VIDEO_LIMIT_MAX_CHARS:
            return True
        STATE.video_limit_input += char
        STATE.dirty = True
        return True

    return False


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

    pygame.mixer.pre_init(
        frequency=CLICK_SAMPLE_RATE,
        size=-16,
        channels=1,
        buffer=256,
    )
    pygame.init()
    pygame.font.init()

    STATE.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("CalSci Latest ITR Simulator")
    STATE.lcd_surface = pygame.Surface((LCD_WIDTH, LCD_HEIGHT), pygame.SRCALPHA)

    _ensure_fonts(get_scale(STATE.screen))
    STATE.key_widgets = _build_key_widgets(STATE.screen)
    _load_click_sound()

    STATE.initialized = True
    render(force=True)


def shutdown_ui():
    _stop_recording_for_exit()
    if not pygame.get_init():
        return
    pygame.quit()


def _set_recent_widget(widget_id: Optional[int]):
    STATE.last_widget_id = widget_id
    STATE.last_key_ts = time.monotonic()
    STATE.dirty = True


def _queue_key(row_idx: int, col_idx: int, widget_id: Optional[int] = None):
    _play_click()
    STATE.pending_keys.append((row_idx, col_idx))
    _set_recent_widget(widget_id)


def _live_keymap():
    try:
        from data_modules.object_handler import keymap as live_keymap  # type: ignore

        return live_keymap
    except Exception:
        return None


def _active_keypad_layout():
    live_keymap = _live_keymap()
    if live_keymap is None:
        return KEYPAD_DEFAULT

    try:
        state = str(getattr(live_keymap, "state", "d") or "d")
        states = getattr(live_keymap, "states", {}) or {}
        layout = states.get(state)
        if layout:
            return layout
    except Exception:
        pass

    return KEYPAD_DEFAULT


def _coord_for_output_in_layout(target: str, layout) -> Optional[tuple[int, int]]:
    target = str(target or "")
    if target == "":
        return None

    for row_idx, row in enumerate(layout):
        for col_idx, value in enumerate(row):
            if value == target:
                return (row_idx, col_idx)

    if len(target) == 1 and target.isalpha():
        folded = target.casefold()
        for row_idx, row in enumerate(layout):
            for col_idx, value in enumerate(row):
                if (
                    isinstance(value, str)
                    and len(value) == 1
                    and value.isalpha()
                    and value.casefold() == folded
                ):
                    return (row_idx, col_idx)

    return None


def _coord_for_key(key: str):
    key = str(key or "")
    if key == "":
        return None

    coord = _coord_for_output_in_layout(key, _active_keypad_layout())
    if coord is not None:
        return coord

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


def _active_widget_ids():
    return {
        widget_id
        for _, _, widget_id in STATE.active_sources.values()
        if widget_id is not None
    }


def _active_key_matches(col_pin: int) -> bool:
    for row_idx, col_idx, _ in STATE.active_sources.values():
        if COL_PINS[col_idx] != col_pin:
            continue
        if STATE.row_levels.get(ROW_PINS[row_idx], 1) == 0:
            return True
    return False


def _press_key_source(source_id: str, row_idx: int, col_idx: int, widget_id: Optional[int] = None):
    next_state = (row_idx, col_idx, widget_id)
    if STATE.active_sources.get(source_id) == next_state:
        return

    STATE.active_sources[source_id] = next_state
    _queue_key(row_idx, col_idx, widget_id=widget_id)


def _release_key_source(source_id: str):
    active = STATE.active_sources.pop(source_id, None)
    if active is None:
        return False

    _set_recent_widget(active[2])
    return True


def _release_all_key_sources():
    if not STATE.active_sources:
        return False

    last_widget_id = None
    for _, _, widget_id in STATE.active_sources.values():
        if widget_id is not None:
            last_widget_id = widget_id

    STATE.active_sources.clear()
    _set_recent_widget(last_widget_id)
    return True


def _queue_key_by_name(key_name: str) -> bool:
    coord = _coord_for_key(key_name)
    if coord is None:
        return False

    row_idx, col_idx = coord
    _queue_key(row_idx, col_idx, widget_id=_widget_id_for_coord(row_idx, col_idx))
    return True


def _press_key_by_name(source_id: str, key_name: str) -> bool:
    coord = _coord_for_key(key_name)
    if coord is None:
        return False

    row_idx, col_idx = coord
    _press_key_source(source_id, row_idx, col_idx, widget_id=_widget_id_for_coord(row_idx, col_idx))
    return True


def _keyboard_source_id(key_code: int) -> str:
    return f"keyboard:{int(key_code)}"


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
    if event.key == pygame.K_v:
        return ("recording_toggle", None)

    key_name = KEYCODE_SHORTCUTS.get(event.key)
    if key_name is not None:
        return ("queue", key_name)

    key_name = PRINTABLE_SHORTCUTS.get(event.unicode)
    if key_name is not None:
        return ("queue", key_name)

    key_name = event.unicode
    if isinstance(key_name, str) and key_name not in ("", "\r", "\n", "\t"):
        return ("queue", key_name)

    return (None, None)


def poll_events():
    ensure_ui()
    _pump_video_recording()
    window_focus_lost = getattr(pygame, "WINDOWFOCUSLOST", None)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            _stop_recording_for_exit()
            raise SystemExit(0)

        if window_focus_lost is not None and event.type == window_focus_lost:
            _release_all_key_sources()
            continue

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if _handle_menu_mouse_down(event.pos):
                continue
            for item in STATE.key_widgets:
                if item.widget.is_clicked(event.pos):
                    if item.row is not None and item.col is not None:
                        _press_key_source("mouse:left", item.row, item.col, widget_id=item.widget_id)
                    else:
                        _play_click()
                        _set_recent_widget(item.widget_id)
                    break

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            _release_key_source("mouse:left")

        if event.type == pygame.KEYDOWN:
            ctrl_held = bool(event.mod & pygame.KMOD_CTRL)

            if event.key == pygame.K_F5:
                _stop_recording_for_exit()
                raise SystemExit(RELOAD_EXIT_CODE)
            if ctrl_held and event.key == pygame.K_q:
                _stop_recording_for_exit()
                raise SystemExit(0)
            if event.key == pygame.K_s:
                _run_screenshot_action()
                continue
            if event.key == pygame.K_v:
                _toggle_recording_action()
                continue
            if _handle_menu_keydown(event):
                continue

            action, payload = _keydown_action(event)

            if action == "quit":
                _stop_recording_for_exit()
                raise SystemExit(0)
            if action == "reload":
                _stop_recording_for_exit()
                raise SystemExit(RELOAD_EXIT_CODE)
            if action == "screenshot":
                _run_screenshot_action()
                continue
            if action == "recording_toggle":
                _toggle_recording_action()
                continue
            if action == "queue" and payload is not None:
                _press_key_by_name(_keyboard_source_id(event.key), payload)

        if event.type == pygame.KEYUP:
            _release_key_source(_keyboard_source_id(event.key))

    if STATE.dirty or (time.monotonic() - STATE.last_key_ts) < PRESS_TOTAL_SECS:
        render(force=False)


def set_row_level(pin: int, value: int):
    STATE.row_levels[pin] = 1 if value else 0


def read_col_pin(col_pin: int) -> int:
    poll_events()

    if STATE.pending_keys:
        row_idx, col_idx = STATE.pending_keys[0]
        expected_col_pin = COL_PINS[col_idx]
        expected_row_pin = ROW_PINS[row_idx]

        if col_pin == expected_col_pin and STATE.row_levels.get(expected_row_pin, 1) == 0:
            STATE.pending_keys.popleft()
            return 0
        return 1

    if _active_key_matches(col_pin):
        return 0

    return 1


def clear_keys():
    STATE.pending_keys.clear()
    _release_all_key_sources()


def pop_pending_keys():
    poll_events()
    items = list(STATE.pending_keys)
    STATE.pending_keys.clear()
    return items


def request_render():
    STATE.dirty = True


def set_invert(enabled: bool):
    STATE.invert = bool(enabled)
    _mark_lcd_dirty()


def set_display_on(enabled: bool):
    STATE.display_on = bool(enabled)
    _mark_lcd_dirty()


def set_all_points_on(enabled: bool):
    STATE.all_points_on = bool(enabled)
    _mark_lcd_dirty()


def clear_framebuffer():
    STATE.framebuffer[:] = b"\x00" * len(STATE.framebuffer)
    _mark_lcd_dirty()


def set_framebuffer(data):
    data = bytes(data)
    STATE.framebuffer[:] = data[: len(STATE.framebuffer)]
    _mark_lcd_dirty()


def write_page_byte(page: int, col: int, value: int):
    if not (0 <= page < 8 and 0 <= col < LCD_WIDTH):
        return
    STATE.framebuffer[page * LCD_WIDTH + col] = value & 0xFF
    _mark_lcd_dirty()


def _draw_lcd_pixels():
    transparent_off_pixels = (
        _load_background_surface() is not None
        or _load_export_template_surface() is not None
    )
    off_color = LCD_OFF_BACKGROUND if transparent_off_pixels else LCD_OFF
    if transparent_off_pixels:
        STATE.lcd_surface.fill((0, 0, 0, 0))
    else:
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
                elif transparent_off_pixels:
                    color = (0, 0, 0, 0)
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


def _draw_recording_indicator(screen, display_rect: pygame.Rect):
    radius = scale_value(10, screen, min_value=4)
    border = max(1, radius // 4)
    margin = scale_value(12, screen, min_value=5)
    center_x = max(radius + margin, min(screen.get_width() - radius - margin, display_rect.right - radius))
    center_y = max(radius + margin, display_rect.y - radius - margin)
    center = (center_x, center_y)

    pygame.draw.circle(screen, (36, 37, 41), center, radius + border)
    pygame.draw.circle(screen, (214, 34, 34), center, radius)

    highlight_radius = max(1, radius // 3)
    highlight = (center_x - highlight_radius, center_y - highlight_radius)
    pygame.draw.circle(screen, (255, 184, 184), highlight, highlight_radius)


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
    live_display_bg = _get_scaled_export_display_background((disp.width, disp.height))
    if live_display_bg is not None:
        STATE.screen.blit(live_display_bg, (disp.x, disp.y))
    scaled_lcd = pygame.transform.scale(STATE.lcd_surface, (disp.width, disp.height))
    STATE.screen.blit(scaled_lcd, (disp.x, disp.y))

    active_widget_ids = _active_widget_ids()
    for item in STATE.key_widgets:
        if item.widget_id in active_widget_ids:
            amount = 1.0
        else:
            amount = _press_amount(now, STATE.last_key_ts) if STATE.last_widget_id == item.widget_id else 0.0
        item.widget.draw(STATE.screen, pressed=amount > 0.0, amount=amount)

    if _recording_active():
        if STATE.recording_frame_dirty:
            _refresh_recording_frame_cache()
        _draw_recording_indicator(STATE.screen, disp)

    _draw_capture_menu(STATE.screen)
    pygame.display.flip()
    STATE.last_render = now
    STATE.dirty = False
    _pump_video_recording(now)
