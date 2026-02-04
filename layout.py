from ui_constants import SCREEN_WIDTH, SCREEN_HEIGHT


def get_scale(screen):
    width, height = screen.get_size()
    if width <= 0 or height <= 0:
        return 1.0
    return min(width / SCREEN_WIDTH, height / SCREEN_HEIGHT)


def scale_value(value, screen, min_value=0):
    scaled = int(round(value * get_scale(screen)))
    return max(min_value, scaled)
