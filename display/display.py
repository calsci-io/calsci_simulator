import random, pygame, sys
from pygame.locals import *

from display.characters import Characters

FPS = 30 # frames per second, the general speed of the program
BOXSIZE = 5 # size of box height & width in pixels
GAPSIZE = 0 # size of gap between boxes in pixels
BOARDWIDTH = 128 # number of columns of icons
BOARDHEIGHT = 64 # number of rows of icons

MARGIN=25

WINDOWWIDTH = BOARDWIDTH*(BOXSIZE+GAPSIZE) + MARGIN # size of window's width in pixels
WINDOWHEIGHT = BOARDHEIGHT*(BOXSIZE+GAPSIZE) + MARGIN# size of windows' height in pixels

# assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.' # what is assert? 
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)

PIXELON=(0, 0, 0)
PIXELOFF=(200, 200, 200)

FPSCLOCK = pygame.time.Clock()

PAGE=6
COL=70

page_col={"PAGE":0,
          "COL":0}


class Display:
    def __init__(self, screen, chrs):
        self.screen=screen
        self.chrs = chrs

    
    def draw_pixel(self,posx, posy, size, color):
        pygame.draw.rect(self.screen, color, (posx, posy, size, size))


    def turn_off_all_pixels(self):
        for i in range(BOARDWIDTH):
            for j in range(BOARDHEIGHT):
                self.draw_pixel(posx=i*(BOXSIZE+GAPSIZE)+XMARGIN, posy=j*(BOXSIZE+GAPSIZE)+YMARGIN, size=BOXSIZE, color=PIXELOFF)
                # print("drawing pixel: ", (i,j))
        
        pygame.display.update()

    def turn_on_all_pixels(self):
        for i in range(BOARDWIDTH):
            for j in range(BOARDHEIGHT):
                self.draw_pixel(posx=i*(BOXSIZE+GAPSIZE)+XMARGIN, posy=j*(BOXSIZE+GAPSIZE)+YMARGIN, size=BOXSIZE, color=PIXELON)
                # print("drawing pixel: ", (i,j))

    def turn_on_pixel(self,x, y):
        self.draw_pixel(posx=x*(BOXSIZE+GAPSIZE)+XMARGIN, posy=y*(BOXSIZE+GAPSIZE)+YMARGIN, size=BOXSIZE, color=PIXELON)


    def turn_off_pixel(self,x, y):
        self.draw_pixel(posx=x*(BOXSIZE+GAPSIZE)+XMARGIN, posy=y*(BOXSIZE+GAPSIZE)+YMARGIN, size=BOXSIZE, color=PIXELOFF)

    def write_data(self,data):
        for i in range(8):
            if data & 1<<i == 1<<i:
                self.turn_on_pixel(page_col["COL"], page_col["PAGE"]*8+i)
            else:
                self.turn_off_pixel(page_col["COL"], page_col["PAGE"]*8+i)

    def reset_cursor(self):
        page_col["PAGE"] = 0
        page_col["COL"] = 0
    def display_print(self,val):
        if page_col["PAGE"] >= 8:
            return
        for a in val:
            character = self.chrs.Chr2bytes(Chr=a)
            for k in character:
                self.write_data(k)
                page_col["COL"]+=1
                pygame.display.update()
            self.write_data(0b00000000)
            page_col["COL"]+=1
            pygame.display.update()

            if page_col["COL"]+2 == BOARDWIDTH:
                page_col["PAGE"]+=1
                page_col["COL"]=0
            if page_col["PAGE"] >= 8:
                return

    # page_col["COL"]=70
    # page_col["PAGE"]=6