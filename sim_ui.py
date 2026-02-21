from __future__ import annotations

import time
from collections import deque

import pygame

LCD_WIDTH = 128
LCD_HEIGHT = 64
LCD_SCALE = 4

KEY_ROWS = 10
KEY_COLS = 5
ROW_PINS = [14, 21, 47, 48, 38, 39, 40, 41, 42, 1]
COL_PINS = [8, 18, 17, 15, 7]

KEY_LABELS = [
    ["on", "alpha", "beta", "home", "wifi"],
    ["bkl", "back", "tool", "diff", "ln"],
    ["left", "down", "right", "ok", "up"],
    ["mod", "bt", "sin", "cos", "tan"],
    ["igtn", "pi", "e", "sum", "frac"],
    ["log", "pow", "sqrt", "sq", "S_D"],
    ["7", "8", "9", "nav_b", "AC"],
    ["4", "5", "6", "*", "/"],
    ["1", "2", "3", "+", "-"],
    [".", "0", ",", "ans", "exe"],
]

WINDOW_BG = (28, 30, 34)
LCD_ON = (18, 33, 40)
LCD_OFF = (198, 214, 226)
BEZEL = (52, 56, 63)
BUTTON_BG = (228, 230, 234)
BUTTON_BORDER = (92, 96, 104)
BUTTON_TEXT = (24, 25, 28)
BUTTON_ACTIVE = (176, 210, 245)

MARGIN = 20
DISPLAY_X = MARGIN
DISPLAY_Y = MARGIN
DISPLAY_W = LCD_WIDTH * LCD_SCALE
DISPLAY_H = LCD_HEIGHT * LCD_SCALE

BUTTON_W = 92
BUTTON_H = 42
BUTTON_GAP = 8
KEYPAD_X = MARGIN
KEYPAD_Y = DISPLAY_Y + DISPLAY_H + 18

WINDOW_W = KEYPAD_X + KEY_COLS * BUTTON_W + (KEY_COLS - 1) * BUTTON_GAP + MARGIN
WINDOW_H = KEYPAD_Y + KEY_ROWS * BUTTON_H + (KEY_ROWS - 1) * BUTTON_GAP + MARGIN


class _UIState:
    def __init__(self):
        self.initialized = False
        self.screen = None
        self.lcd_surface = None
        self.font = None
        self.small_font = None
        self.key_rects = {}
        self.pending_keys = deque()
        self.last_key = None
        self.last_key_ts = 0.0
        self.row_levels = {pin: 1 for pin in ROW_PINS}

        self.framebuffer = bytearray(LCD_WIDTH * LCD_HEIGHT // 8)
        self.invert = False
        self.display_on = True
        self.all_points_on = False

        self.dirty = True
        self.last_render = 0.0


STATE = _UIState()


def ensure_ui():
    if STATE.initialized:
        return

    pygame.init()
    pygame.font.init()

    STATE.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("CalSci Latest ITR Simulator")
    STATE.lcd_surface = pygame.Surface((LCD_WIDTH, LCD_HEIGHT))
    STATE.font = pygame.font.Font(None, 20)
    STATE.small_font = pygame.font.Font(None, 16)

    for row in range(KEY_ROWS):
        for col in range(KEY_COLS):
            x = KEYPAD_X + col * (BUTTON_W + BUTTON_GAP)
            y = KEYPAD_Y + row * (BUTTON_H + BUTTON_GAP)
            STATE.key_rects[(row, col)] = pygame.Rect(x, y, BUTTON_W, BUTTON_H)

    STATE.initialized = True
    render(force=True)


def _queue_key(row_idx: int, col_idx: int):
    STATE.pending_keys.append((row_idx, col_idx))
    STATE.last_key = (row_idx, col_idx)
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
            for (row, col), rect in STATE.key_rects.items():
                if rect.collidepoint(event.pos):
                    _queue_key(row, col)
                    break

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q and (event.mod & pygame.KMOD_CTRL):
                raise SystemExit(0)
            shortcut = _keyboard_shortcuts().get(event.key)
            if shortcut:
                _queue_key(shortcut[0], shortcut[1])

    # Keep the UI responsive and refresh on state changes.
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
        col_base = x
        for page in range(8):
            value = STATE.framebuffer[page * LCD_WIDTH + col_base]
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

    _draw_lcd_pixels()

    STATE.screen.fill(WINDOW_BG)

    bezel_rect = pygame.Rect(DISPLAY_X - 8, DISPLAY_Y - 8, DISPLAY_W + 16, DISPLAY_H + 16)
    pygame.draw.rect(STATE.screen, BEZEL, bezel_rect, border_radius=12)

    scaled = pygame.transform.scale(STATE.lcd_surface, (DISPLAY_W, DISPLAY_H))
    STATE.screen.blit(scaled, (DISPLAY_X, DISPLAY_Y))

    for row in range(KEY_ROWS):
        for col in range(KEY_COLS):
            rect = STATE.key_rects[(row, col)]
            active = STATE.last_key == (row, col) and (now - STATE.last_key_ts) < 0.15
            fill = BUTTON_ACTIVE if active else BUTTON_BG
            pygame.draw.rect(STATE.screen, fill, rect, border_radius=8)
            pygame.draw.rect(STATE.screen, BUTTON_BORDER, rect, width=1, border_radius=8)

            label = KEY_LABELS[row][col]
            text = STATE.small_font.render(label, True, BUTTON_TEXT)
            text_rect = text.get_rect(center=rect.center)
            STATE.screen.blit(text, text_rect)

    title = STATE.font.render("CalSci Latest ITR Simulator (desktop)", True, (232, 236, 244))
    STATE.screen.blit(title, (MARGIN, 2))

    pygame.display.flip()
    STATE.last_render = now
    STATE.dirty = False
