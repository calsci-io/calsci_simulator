import pygame
class Button:
    def __init__(self,text, width=60, height=60, pos_x=0, pos_y=0):
        self.text = text
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("Arial", 10)
        self.rect = None
        self.pos_x = pos_x
        self.pos_y = pos_y


    def draw(self, screen, x, y):
        position_x = x * self.width+1
        position_y = y * self.height+1

        self.rect = pygame.Rect(position_x, position_y, self.width-1, self.height-1)
        pygame.draw.rect(screen, (255,255,255), self.rect)

        text = self.font.render(self.text, True, (20,20,20), (255,255,255))
        rect = text.get_rect()
        rect.topleft = (position_x+self.width//2-text.get_width()//2, position_y+self.height//2-text.get_height()//2)
        
        screen.blit(text, rect)
        
    def is_clicked(self, pos):
       return self.rect.collidepoint(pos)


    def get_text(self):
        return self.text 
