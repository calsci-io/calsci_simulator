import pygame
pygame.init()
pygame.font.init()
pygame.display.set_caption("CalSci Simulator")
import ui as rc
from ui import Button
from utility.keymap import Keypad
from utility.constants import KeyButtons as KB, KeypadMode as KM
from display.display import Display, WINDOWHEIGHT, page_col
from display.characters import Characters 
from display.text_buffer import TextBuffer
from display.text_uploader import TextUploader
from data_modules.object_handler import keypad_state_manager_reset, screen, keypad, Typer, clock
from process_modules.app_runner import app_runner
from utility.typer import get_buttons, get_other_buttons
import data_modules.object_handler as oh

# screen = pygame.display.set_mode((450, 800))
# screen.fill((240, 240, 240))
display = Display(screen=screen, chrs=Characters())

typer = Typer(keypad=keypad, keypad_map=None )
display.turn_off_all_pixels()
text = TextBuffer()
text_uploader = TextUploader(display, chrs=Characters(), t_b=text)
text_uploader.refresh()
text.all_clear()
# main_font = pygame.font.Font("DejaVuSans.ttf", 14)
# fallback_font = pygame.font.Font("notosymbols2.ttf", 14)
# emoji_font = pygame.font.Font("notoemoji.ttf", 14)
# clock = pygame.time.Clock()
while True:    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    #     if event.type == pygame.MOUSEBUTTONDOWN:
    #         if event.button != 1:
    #             continue
            
            # x = typer.start_typing()
            
            # if x == "alpha" or x == "beta":
            #     typer.change_keymaps(x)
            #     state = typer.keypad.state
            #     if(state==KM.DEFAULT):
            #         text_uploader.refresh()
            #     else:
            #         text_uploader.refresh(state=x)
            #     text.update_buffer("")
            #     continue

            # if x == "AC":
            #     text.all_clear()
            #     text_uploader.refresh()
            #     display.clear_display()

            # if x != "ans":
            #     print(x)
            #     text.update_buffer(x)


            # text_uploader.refresh() 
    rc.present()
    keypad_state_manager_reset()
    app_runner()

    # button_posx = 20
    # button_posy = 20

    # width = 40
    # height = 40
    # gap = 2

    # text = main_font.render("A", True, (20,20,20), (240,240,240))
    # rect_text = text.get_rect()
    # rect_text.topleft = (button_posx, button_posy-text.get_height()-gap)
    # screen.blit(text,rect_text)

    # text = main_font.render("B", True, (20,20,20), (240,240,240))
    # rect_text = text.get_rect()
    # rect_text.topleft = (button_posx+width-text.get_width(), button_posy-text.get_height()-gap)
    # screen.blit(text,rect_text)


    # rect = pygame.Rect(button_posx,button_posy,width,height)
    # pygame.draw.rect(screen, (255,255,255), rect)
    # text = main_font.render("K", True, (20,20,20), (255,255,255))
    # rect_text = text.get_rect()
    # rect_text.topleft = (button_posx+width//2-text.get_width()//2, button_posy+height//2-text.get_height()//2)

    # screen.blit(text,rect_text)


    rc.present()

    clock.tick(60)
    
