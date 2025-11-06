import pygame
from constants import KeyButtons as KB
from components import Button

def draw_nav_buttons(screen, x=400, y=400):

    NAV_U_BUTTON = Button(text=KB.NAV_U, width=50, height=25, pos_x=75-25, pos_y=0)
    NAV_D_BUTTON = Button(text=KB.NAV_D, width=50, height=25, pos_x=75-25, pos_y=125)
    NAV_L_BUTTON = Button(text=KB.NAV_L, width=40, height=50, pos_x=0, pos_y=75-25)
    NAV_R_BUTTON = Button(text=KB.NAV_R, width=40, height=50, pos_x=115, pos_y=75-25)
    OK_BUTTON = Button(text=KB.OK, width=50, height=50, pos_x=75-25, pos_y=75-25)

    buttons = []

    buttons.append(NAV_U_BUTTON)
    buttons.append(NAV_D_BUTTON)
    buttons.append(NAV_L_BUTTON)
    buttons.append(NAV_R_BUTTON)
    buttons.append(OK_BUTTON)
    
    for button in buttons:
        button.draw(screen, x, y) 

    return buttons

    
