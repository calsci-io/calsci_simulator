import pygame

main_font = pygame.font.Font("DejaVuSans.ttf", 14)
fallback_font = pygame.font.Font("notosymbols2.ttf", 14)
emoji_font = pygame.font.Font("notoemoji.ttf", 14)
class Button:
    def __init__(self,text, width=60, height=60, pos_x=0, pos_y=0, enabled=False):
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


    def draw(self, screen):
        position_x = self.pos_x+1
        position_y = self.pos_y+1
        bg_color = (255,255,255)
        if self.enabled:
            bg_color = (200,200,200)

        self.rect = pygame.Rect(position_x, position_y, self.width-1, self.height-1)
        pygame.draw.rect(screen, bg_color, self.rect)

        
        text = self.font.render(self.text, True, (20,20,20), bg_color)
        metrics = self.font.metrics(self.text)
        
        if metrics is None and metrics[0] is None:
            text = self.fallback_font.render(self.text, True, (20,20,20), bg_color)
        metrics = self.fallback_font.metrics(self.text)

        if self.text == "⧉" or self.text == "📋" or self.text == "🧰" or self.text == "📶" or self.text == "🔆" or self.text=="🅱":
            text = self.emoji_font.render(self.text, True, (20,20,20), bg_color)

        rect = text.get_rect()
        rect.topleft = (position_x+self.width//2-text.get_width()//2, position_y+self.height//2-text.get_height()//2)
        
        screen.blit(text, rect)
        
    def is_clicked(self, pos):
       return self.rect.collidepoint(pos)


    def get_text(self):
        return self.text 
