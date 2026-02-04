import pygame
import os
# import subprocess

# subprocess.Popen(
#     ["wmctrl", "-r", ":ACTIVE:", "-e", "0,0,0,960,-1"],
#     stdout=subprocess.DEVNULL,
#     stderr=subprocess.DEVNULL
# )


pygame.display.init()
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h

# 3. Calculate position for the right side
# Subtract window width from screen width to align to the right edge
x_pos = screen_width - 455 # 50px padding from the edge
y_pos = 75                             # Distance from top

# subprocess.Popen(
#     [f"wmctrl", "-r", ":ACTIVE:", "-e", "0,0,0,{x_pos},-1"],
#     stdout=subprocess.DEVNULL,
#     stderr=subprocess.DEVNULL
# )

# 4. Set the environment variable BEFORE full initialization
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x_pos},{y_pos}"
os.environ["SDL_VIDEO_ALLOW_SCREENSAVER"] = "1"
os.environ["SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS"] = "0"
os.environ["SDL_HINT_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR"] = "0"

pygame.init()
pygame.font.init()
pygame.display.set_caption("CalSci")
from components import Button
from keymap import Keypad
from constants import KeyButtons as KB, KeypadMode as KM
from display.display import Display, WINDOWHEIGHT, page_col
from display.characters import Characters 
from display.text_buffer import TextBuffer
from display.text_uploader import TextUploader
from data_modules.object_handler import keypad_state_manager_reset, screen, keypad, Typer, clock
from process_modules.app_runner import app_runner


# import os
# # import pygame

# WINDOW_WIDTH = 800
# WINDOW_HEIGHT = 600

# # Assume screen width (common values: 1366, 1920, etc.)
# SCREEN_WIDTH = 1920   # change if needed

# x_pos = SCREEN_WIDTH - WINDOW_WIDTH
# y_pos = 100  # top margin

# os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x_pos},{y_pos}"

# import watcher

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
    pygame.display.update()
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


    pygame.display.update()

    clock.tick(60)
    