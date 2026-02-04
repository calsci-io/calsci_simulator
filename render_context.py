import pygame

from ui_constants import SCREEN_WIDTH, SCREEN_HEIGHT

BASE_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
WINDOW_FLAGS = 0

# Display window and render surface share the same size.
window = pygame.display.set_mode(BASE_SIZE, WINDOW_FLAGS)
screen = window


def present():
    pygame.display.update()


def map_input_pos(pos):
    return pos
