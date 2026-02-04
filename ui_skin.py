import pygame
from ui_constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    DISPLAY_TOP_MARGIN,
    DISPLAY_BEZEL_PADDING,
    CASE_PADDING,
    CASE_RADIUS,
)
from display.display import get_display_metrics
from layout import scale_value

CASE_DARK = (24, 26, 30)
CASE_MID = (36, 38, 43)
CASE_LIGHT = (52, 54, 60)
BEZEL_DARK = (22, 23, 27)
BEZEL_MID = (36, 38, 42)
LABEL_BG = (230, 230, 230)
LABEL_TEXT = (40, 40, 40)
LABEL_FONT_SIZE = 16


def _display_rect(screen):
    _, _, display_w, display_h = get_display_metrics(screen)
    x = (screen.get_width() - display_w) // 2
    y = scale_value(DISPLAY_TOP_MARGIN, screen, min_value=0)
    return pygame.Rect(x, y, display_w, display_h)


def draw_shell(screen):
    w, h = screen.get_size()
    if (w, h) != (SCREEN_WIDTH, SCREEN_HEIGHT):
        # Keep layout stable even if window size changes.
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
    label_font = pygame.font.Font("DejaVuSans.ttf", max(8, scale_value(LABEL_FONT_SIZE, screen, min_value=1)))
    text = label_font.render("CalSci", True, LABEL_TEXT)
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
