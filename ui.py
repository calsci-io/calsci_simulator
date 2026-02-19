"""
CalSci UI Module
================
Single modular UI file for the CalSci simulator.
Organized into sections for easy maintenance.
"""

import pygame

# =============================================================================
# CONSTANTS
# =============================================================================

SCREEN_WIDTH = 450
SCREEN_HEIGHT = 950

DISPLAY_TOP_MARGIN = 85
DISPLAY_BEZEL_PADDING = 16
DISPLAY_SIDE_PADDING = 16

CASE_PADDING = 10
CASE_RADIUS = 32

KEYPAD_TOP_GAP = 14
SYSTEM_TO_MAIN_GAP = 12

# Colors
CASE_DARK = (24, 26, 30)
CASE_MID = (36, 38, 43)
CASE_LIGHT = (52, 54, 60)
BEZEL_DARK = (22, 23, 27)
BEZEL_MID = (36, 38, 42)
LABEL_BG = (230, 230, 230)
LABEL_TEXT = (40, 40, 40)
LABEL_FONT_SIZE = 16


# =============================================================================
# LAYOUT / SCALING
# =============================================================================

def get_scale(screen):
    """Calculate scale factor based on screen size."""
    width, height = screen.get_size()
    if width <= 0 or height <= 0:
        return 1.0
    return min(width / SCREEN_WIDTH, height / SCREEN_HEIGHT)


def scale_value(value, screen, min_value=0):
    """Scale a value according to current screen size."""
    scaled = int(round(value * get_scale(screen)))
    return max(min_value, scaled)


# =============================================================================
# RENDER CONTEXT
# =============================================================================

BASE_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
WINDOW_FLAGS = 0

window = pygame.display.set_mode(BASE_SIZE, WINDOW_FLAGS)
screen = window


def present():
    """Update the display."""
    pygame.display.update()


def map_input_pos(pos):
    """Map input position (for future scaling support)."""
    return pos


# =============================================================================
# FONTS
# =============================================================================

main_font = None
label_font = None
tiny_label_font = None
fallback_font = None
emoji_font = None
_last_scale = None


def init_fonts():
    """Initialize fonts (call after pygame.font.init())."""
    global main_font, label_font, tiny_label_font, fallback_font, emoji_font
    main_font = pygame.font.Font("assets/DejaVuSans.ttf", 14)
    label_font = pygame.font.Font("assets/DejaVuSans.ttf", 12)
    tiny_label_font = pygame.font.Font("assets/DejaVuSans.ttf", 9)
    fallback_font = pygame.font.Font("assets/notosymbols2.ttf", 14)
    emoji_font = pygame.font.Font("assets/notoemoji.ttf", 14)


def _ensure_fonts(scale):
    """Ensure fonts are scaled correctly."""
    global main_font, label_font, tiny_label_font, fallback_font, emoji_font, _last_scale
    if _last_scale == scale:
        return
    main_size = max(8, int(round(14 * scale)))
    label_size = max(7, int(round(12 * scale)))
    tiny_size = max(6, int(round(9 * scale)))
    main_font = pygame.font.Font("assets/DejaVuSans.ttf", main_size)
    label_font = pygame.font.Font("assets/DejaVuSans.ttf", label_size)
    tiny_label_font = pygame.font.Font("assets/DejaVuSans.ttf", tiny_size)
    fallback_font = pygame.font.Font("assets/notosymbols2.ttf", main_size)
    emoji_font = pygame.font.Font("assets/notoemoji.ttf", main_size)
    _last_scale = scale


# =============================================================================
# SHELL / SKIN
# =============================================================================

def _display_rect(screen):
    """Get the display rectangle."""
    from display.display import get_display_metrics
    _, _, display_w, display_h = get_display_metrics(screen)
    x = (screen.get_width() - display_w) // 2
    y = scale_value(DISPLAY_TOP_MARGIN, screen, min_value=0)
    return pygame.Rect(x, y, display_w, display_h)


def draw_shell(screen):
    """Draw the calculator shell/case."""
    w, h = screen.get_size()
    if (w, h) != (SCREEN_WIDTH, SCREEN_HEIGHT):
        w = screen.get_width()
        h = screen.get_height()

    screen.fill(CASE_DARK)

    case_padding = scale_value(CASE_PADDING, screen, min_value=0)
    case_radius = scale_value(CASE_RADIUS, screen, min_value=0)
    outer = pygame.Rect(case_padding, case_padding, w - 2 * case_padding, h - 2 * case_padding)
    pygame.draw.rect(screen, CASE_DARK, outer, border_radius=case_radius)

    mid = outer.inflate(-scale_value(8, screen, min_value=0), -scale_value(8, screen, min_value=0))
    pygame.draw.rect(screen, CASE_MID, mid, border_radius=max(0, case_radius - scale_value(6, screen, min_value=0)))

    inner = mid.inflate(-scale_value(6, screen, min_value=0), -scale_value(6, screen, min_value=0))
    pygame.draw.rect(screen, CASE_LIGHT, inner, border_radius=max(0, case_radius - scale_value(10, screen, min_value=0)))

    # Brand label
    label_w = scale_value(90, screen, min_value=1)
    label_h = scale_value(26, screen, min_value=1)
    label_x = w // 2 - label_w // 2
    label_y = case_padding + scale_value(8, screen, min_value=0)
    label_radius = scale_value(6, screen, min_value=0)
    pygame.draw.rect(screen, LABEL_BG, (label_x, label_y, label_w, label_h), border_radius=label_radius)
    lbl_font = pygame.font.Font("assets/DejaVuSans.ttf", max(8, scale_value(LABEL_FONT_SIZE, screen, min_value=1)))
    text = lbl_font.render("CalSci", True, LABEL_TEXT)
    screen.blit(text, text.get_rect(center=(label_x + label_w // 2, label_y + label_h // 2)))

    # Display bezel
    disp = _display_rect(screen)
    bezel_pad = scale_value(DISPLAY_BEZEL_PADDING, screen, min_value=0)
    bezel = disp.inflate(bezel_pad * 2, bezel_pad * 2)
    bezel_radius = scale_value(14, screen, min_value=0)
    pygame.draw.rect(screen, BEZEL_MID, bezel, border_radius=bezel_radius)
    pygame.draw.rect(screen, BEZEL_DARK, bezel, width=2, border_radius=bezel_radius)

    # Slight shadow under display area
    shadow = bezel.move(0, scale_value(3, screen, min_value=0))
    pygame.draw.rect(screen, (18, 19, 21), shadow, width=2, border_radius=bezel_radius)


# =============================================================================
# COMPONENTS
# =============================================================================

class Button:
    """Basic button component."""

    def __init__(self, text, width=60, height=60, pos_x=0, pos_y=0, enabled=False, shape="rect"):
        self.text = text
        self.width = width
        self.height = height
        self.font = main_font
        self.fallback_font = fallback_font
        self.emoji_font = emoji_font
        self.rect = None
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.enabled = enabled
        self.shape = shape

    def draw(self, screen, pressed=False):
        _ensure_fonts(get_scale(screen))
        self.font = main_font
        self.fallback_font = fallback_font
        self.emoji_font = emoji_font
        position_x = self.pos_x
        position_y = self.pos_y
        if self.shape == "circle":
            radius = min(self.width, self.height) // 2
        else:
            radius = max(4, min(8, self.height // 5))
        base_color = (230, 230, 230)
        if pressed:
            base_color = (200, 200, 200)
        if self.enabled:
            base_color = (205, 205, 205)
        shadow_color = (140, 140, 140)
        border_color = (85, 85, 85)
        shadow_offset = 2
        text_offset = 0
        if pressed:
            shadow_color = (95, 95, 95)
            border_color = (55, 55, 55)
            shadow_offset = 0
            text_offset = max(1, int(round(2 * get_scale(screen))))

        shadow = pygame.Rect(position_x, position_y + shadow_offset, self.width, self.height)
        pygame.draw.rect(screen, shadow_color, shadow, border_radius=radius)

        self.rect = pygame.Rect(position_x, position_y, self.width, self.height)
        pygame.draw.rect(screen, base_color, self.rect, border_radius=radius)
        pygame.draw.rect(screen, border_color, self.rect, width=1, border_radius=radius)

        text = self.get_text_font(self.text, (0, 0, 0), None)

        rect = text.get_rect()
        rect.topleft = (
            position_x + self.width // 2 - text.get_width() // 2,
            position_y + self.height // 2 - text.get_height() // 2 + text_offset,
        )
        screen.blit(text, rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def get_text(self, state="d"):
        return self.text

    def get_text_font(self, text, text_color, bg_color=None, small=False, tiny=False):
        if tiny:
            font = tiny_label_font
        else:
            font = label_font if small else self.font

        metrics = font.metrics(text)
        if metrics is None or any(m is None for m in metrics):
            font = self.fallback_font

        emoji_chars = ["🗐", "📋", "🧰", "📶", "🔆", "🅱"]
        if text in emoji_chars:
            font = self.emoji_font

        if bg_color is None:
            return font.render(text, True, text_color)
        return font.render(text, True, text_color, bg_color)


class OtherButton(Button):
    """Button with alpha and beta text labels."""

    def __init__(self, text, alpha_text, beta_text, width=60, height=60, pos_x=0, pos_y=0, enabled=False):
        self.text = text
        self.alpha_text = alpha_text
        self.beta_text = beta_text
        self.width = width
        self.height = height
        self.font = main_font
        self.fallback_font = fallback_font
        self.emoji_font = emoji_font
        self.rect = None
        self.pos_x = pos_x
        self.pos_y = pos_y

    def draw(self, screen, state, pressed=False):
        _ensure_fonts(get_scale(screen))
        self.font = main_font
        self.fallback_font = fallback_font
        self.emoji_font = emoji_font
        pad = max(2, int(round(4 * get_scale(screen))))
        text_offset = max(1, int(round(2 * get_scale(screen)))) if pressed else 0
        alpha_color = (0, 0, 0)
        beta_color = (0, 0, 0)

        self.rect = pygame.Rect(self.pos_x, self.pos_y, self.width, self.height)
        radius = max(4, min(10, self.height // 5))
        shadow_offset = 2
        shadow_color = (140, 140, 140)
        border_color = (85, 85, 85)
        base_color = (230, 230, 230)
        if pressed:
            shadow_offset = 0
            shadow_color = (95, 95, 95)
            border_color = (55, 55, 55)
            base_color = (200, 200, 200)
        shadow = self.rect.move(0, shadow_offset)
        pygame.draw.rect(screen, shadow_color, shadow, border_radius=radius)
        pygame.draw.rect(screen, base_color, self.rect, border_radius=radius)
        pygame.draw.rect(screen, border_color, self.rect, width=1, border_radius=radius)

        if self.alpha_text:
            alpha_is_tiny = self.alpha_text.lower() in {"caps", "undo"}
            alpha_is_caps = self.alpha_text.lower() == "caps"
            text = self.get_text_font(self.alpha_text, alpha_color, None, small=True, tiny=alpha_is_tiny)
            rect_text = text.get_rect()
            rect_text.topleft = (
                self.pos_x + pad - (1 if alpha_is_caps else 0),
                self.pos_y + pad + (1 if alpha_is_tiny else 0) + text_offset,
            )
            screen.blit(text, rect_text)

        if self.beta_text:
            beta_is_tiny = self.beta_text.lower() in {"caps", "undo"}
            beta_is_undo = self.beta_text.lower() == "undo"
            text = self.get_text_font(self.beta_text, beta_color, None, small=True, tiny=beta_is_tiny)
            rect_text = text.get_rect()
            rect_text.topright = (
                self.pos_x + self.width - pad + (1 if beta_is_undo else 0),
                self.pos_y + pad + (1 if beta_is_tiny else 0) + text_offset,
            )
            screen.blit(text, rect_text)

        text = self.get_text_font(self.text, (0, 0, 0), None)
        rect_text = text.get_rect()
        rect_text.midbottom = (self.pos_x + self.width // 2, self.pos_y + self.height - pad + text_offset)
        screen.blit(text, rect_text)

    def get_text(self, state="d"):
        if state == "a" and self.alpha_text:
            return self.alpha_text
        elif state == "b" and self.beta_text:
            return self.beta_text
        return self.text

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
