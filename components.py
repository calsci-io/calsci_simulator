import pygame
from layout import get_scale

main_font = pygame.font.Font("DejaVuSans.ttf", 14)
label_font = pygame.font.Font("DejaVuSans.ttf", 12)
tiny_label_font = pygame.font.Font("DejaVuSans.ttf", 9)
fallback_font = pygame.font.Font("notosymbols2.ttf", 14)
emoji_font = pygame.font.Font("notoemoji.ttf", 14)
_last_scale = None


def _ensure_fonts(scale):
    global main_font, label_font, tiny_label_font, fallback_font, emoji_font, _last_scale
    if _last_scale == scale:
        return
    main_size = max(8, int(round(14 * scale)))
    label_size = max(7, int(round(12 * scale)))
    tiny_size = max(6, int(round(9 * scale)))
    main_font = pygame.font.Font("DejaVuSans.ttf", main_size)
    label_font = pygame.font.Font("DejaVuSans.ttf", label_size)
    tiny_label_font = pygame.font.Font("DejaVuSans.ttf", tiny_size)
    fallback_font = pygame.font.Font("notosymbols2.ttf", main_size)
    emoji_font = pygame.font.Font("notoemoji.ttf", main_size)
    _last_scale = scale

class Button:
    def __init__(self, text, width=60, height=60, pos_x=0, pos_y=0, enabled=False, shape="rect"):
        self.text = text
        self.width = width
        self.height = height
        self.font = main_font 
        self.fallback_font =fallback_font 
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

        # No glossy highlight; keep a flat key surface.

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
        # choose font size
        if tiny:
            font = tiny_label_font
        else:
            font = label_font if small else self.font

        metrics = font.metrics(text)
        if metrics is None or any(m is None for m in metrics):
            font = self.fallback_font

        # emoji override list
        emoji_chars = ["🗐", "📋", "🧰", "📶", "🔆", "🅱"]
        if text in emoji_chars:
            font = self.emoji_font

        if bg_color is None:
            return font.render(text, True, text_color)
        return font.render(text, True, text_color, bg_color)

class OtherButton(Button):
    def __init__(self,text, alpha_text, beta_text, width=60, height=60, pos_x=0, pos_y=0, enabled=False):
        self.text = text
        self.alpha_text = alpha_text
        self.beta_text = beta_text
        self.width = width
        self.height = height
        self.font = main_font 
        self.fallback_font =fallback_font 
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
        # No glossy highlight; keep a flat key surface.

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
        # print("Testing buttong press")
        return self.rect.collidepoint(pos)
