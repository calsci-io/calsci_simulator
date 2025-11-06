import pygame
pygame.init()
pygame.font.init()
pygame.display.set_caption("Keyboard")
from components import Button
from keymap import Keypad
from constants import KeyButtons as KB, KeypadMode as KM
from display.display import Display, WINDOWHEIGHT, page_col
from display.characters import Characters 
from display.text_buffer import TextBuffer
from display.text_uploader import TextUploader
from data_modules.object_handler import keypad_state_manager_reset, screen, keypad, Typer, clock
from process_modules.app_runner import app_runner

from data_modules.object_handler import buttons


display = Display(screen=screen, chrs=Characters())

typer = Typer(keypad=keypad, keypad_map=None )
display.turn_off_all_pixels()
text = TextBuffer()
text_uploader = TextUploader(display, chrs=Characters(), t_b=text)
text_uploader.refresh()
text.all_clear()

while True:    
    # for event in pygame.event.get():
    #     if event.type == pygame.QUIT:
    #         pygame.quit()
    #         quit()
        
    #     if event.type == pygame.MOUSEBUTTONDOWN:
    #         if event.button != 1:
    #             continue
            
    #         x = typer.start_typing()
            
    #         if x == "alpha" or x == "beta":
    #             typer.change_keymaps(x)
    #             state = typer.keypad.state
    #             if(state==KM.DEFAULT):
    #                 text_uploader.refresh()
    #             else:
    #                 text_uploader.refresh(state=x)
    #             text.update_buffer("")
    #             continue

    #         if x == "AC":
    #             text.all_clear()
    #             text_uploader.refresh()
    #             display.clear_display()

    #         if x != "ans":
    #             print(x)
    #             text.update_buffer(x)

    x = typer.start_typing()

    if x:
        print(x)
        text.update_buffer(x)
        text_uploader.refresh()


    #         text_uploader.refresh() 
    # pygame.display.update()
    # keypad_state_manager_reset()
    # app_runner()


    pygame.display.update()

    clock.tick(60)
    