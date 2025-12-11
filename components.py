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

        text = self.get_text_font(self.text, (20,20,20), bg_color)

        rect = text.get_rect()
        rect.topleft = (position_x+self.width//2-text.get_width()//2, position_y+self.height//2-text.get_height()//2)
        
        screen.blit(text, rect)
        
    def is_clicked(self, pos):
       return self.rect.collidepoint(pos)


    def get_text(self, state="d"):
        return self.text 
    
    def get_text_font(self, text, text_color, bg_color):
    # try main font
        metrics = self.font.metrics(text)

        if metrics is None:
            # fallback font if unsupported
            text_obj = self.fallback_font.render(text, True, text_color, bg_color)
            metrics = self.fallback_font.metrics(text)
        else:
            text_obj = self.font.render(text, True, text_color, bg_color)

        # emoji override list
        emoji_chars = ["🗐", "📋", "🧰", "📶", "🔆", "🅱"]

        if text in emoji_chars:
            text_obj = self.emoji_font.render(text, True, text_color, bg_color)

        return text_obj

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
    
    def draw(self, screen, state):
        gap = 2
        text_color = (20,20,20)
        if state=="a":
            text_color = (255,0,0)
        # print(self.alpha_text)
        text = self.get_text_font(self.alpha_text, text_color, (240,240,240))
        
        rect_text = text.get_rect()
        rect_text.topleft = (self.pos_x, self.pos_y-text.get_height()-gap)
        rect = pygame.Rect(self.pos_x, self.pos_y-text.get_height()-gap, self.width+1, self.width+1)
        pygame.draw.rect(screen, (240,240,240), rect)
        screen.blit(text,rect_text)

        text_color = (20,20,20)
        if state=="b":
            text_color = (255,0,0)

        text = self.get_text_font(self.beta_text, text_color, (240,240,240))
        rect_text = text.get_rect()
        rect_text.topleft = (self.pos_x+self.width-text.get_width(), self.pos_y-text.get_height()-gap)
        rect = pygame.Rect(self.pos_x+self.width-text.get_width(), self.pos_y-text.get_height()-gap, self.width+1, self.width+1)
        pygame.draw.rect(screen, (240,240,240), rect)


        screen.blit(text,rect_text)

        text_color = (20,20,20)
        self.rect = pygame.Rect(self.pos_x,self.pos_y,self.width,self.height)
        pygame.draw.rect(screen, (255,255,255), self.rect)
        text = self.get_text_font(self.text, text_color, (255,255,255))
        rect_text = text.get_rect()
        rect_text.topleft = (self.pos_x+self.width//2-text.get_width()//2, self.pos_y+self.height//2-text.get_height()//2)
        

        screen.blit(text,rect_text)


    def get_text(self, state="d"):
        if state == "a" and self.alpha_text:
            return self.alpha_text
        elif state == "b" and self.beta_text:
            return self.beta_text
        
        return self.text
    
    def is_clicked(self, pos):
        # print("Testing buttong press")
        return self.rect.collidepoint(pos)
