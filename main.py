import pygame
from components import Button
from keymap import Keypad
from constants import KeyButtons as KB, KeypadMode as KM
from display.display import Display, WINDOWHEIGHT, thread
from display.characters import Characters 

pygame.init()
pygame.font.init()


screen = pygame.display.set_mode((670, 1001))
pygame.display.set_caption("Keyboard")
clock = pygame.time.Clock()
keypad = Keypad()

screen.fill((240, 240, 240))


def draw_buttons():
    buttons = []
    for x in range(5):
        for y in range(10):
            button = Button(text=keypad.key_out(x,y))
            buttons.append(button)
            button.draw(screen, 3+x, WINDOWHEIGHT//50+y)

    return buttons    

buttons = draw_buttons()


class Typer:
    def __init__(self,keypad, keypad_map, buttons):
        self.keypad = keypad
        self.keypad_map = keypad_map
        self.buttons = buttons

    def start_typing(self, pos):
            # pos = pygame.mouse.get_pos()
            # if pygame.mouse.get_pressed()[0]!=1:
            #    return None 
            for button in self.buttons:
                if button.is_clicked(pos):
                    key = button.get_text()
                    print("key pressed:", key)
                    if key == KB.ALPHA:
                        if self.keypad.state == KM.ALPHA:
                            self.keypad.key_change(KM.DEFAULT)
                        else:
                            self.keypad.key_change(KM.ALPHA)

                        self.buttons = draw_buttons()
                        return None
                    
                    if key == KB.BETA:
                        if self.keypad.state == KM.BETA:
                            self.keypad.key_change(KM.DEFAULT)
                        else:
                            self.keypad.key_change(KM.BETA)
                        
                        self.buttons = draw_buttons()
                        return None
                    return key

display = Display(screen=screen, chrs=Characters())

typer = Typer(keypad=keypad, keypad_map=None, buttons=buttons)
temp = ""
display.turn_off_all_pixels()

while True:    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button != 1:
                continue
            text = typer.start_typing(event.pos)
            if text=="AC":
                display.turn_off_all_pixels()
                display.reset_cursor()
                temp=""
                continue 
            if text:
                temp+=text
                surfaces = display.display_print(text)
                screen.blits(surfaces)



    pygame.display.update()

    clock.tick(60)
    