import random, pygame, sys
from pygame.locals import *

from display.characters import Characters

FPS = 60 # frames per second, the general speed of the program
BOXSIZE = 3 # size of box height & width in pixels
GAPSIZE = 0 # size of gap between boxes in pixels
BOARDWIDTH = 128 # number of columns of icons
BOARDHEIGHT = 64 # number of rows of icons

MARGIN=70

WINDOWWIDTH = BOARDWIDTH*(BOXSIZE+GAPSIZE) + MARGIN # size of window's width in pixels
WINDOWHEIGHT = BOARDHEIGHT*(BOXSIZE+GAPSIZE) + MARGIN# size of windows' height in pixels

# assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.' # what is assert? 
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)

PIXELON=(0, 0, 0)
PIXELOFF=(200, 200, 200)
# PIXELOFF=(146, 146, 146)
# PIXELOFF=(230, 230, 230)

FPSCLOCK = pygame.time.Clock()

page_col={"PAGE":0,
          "COL":0}

class Display:
    def __init__(self, screen, chrs):
        self.screen=screen
        self.chrs = chrs

    
    def draw_pixel(self,posx, posy, size, color):
        pygame.draw.rect(self.screen, color, (posx, posy, size, size))

    def clear_display(self):
        self.turn_off_all_pixels()
        pygame.display.update()

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

    def get_pos(self,x,y):
        return (x*(BOXSIZE+GAPSIZE)+XMARGIN, y*(BOXSIZE+GAPSIZE)+YMARGIN)

    def write_data(self,data):
        if page_col["PAGE"] >= 8:
            return
        # data_queue.put((data, self.get_pos(page_col["COL"], page_col["PAGE"]*8)))
        surface = pygame.Surface((1*BOXSIZE,8*BOXSIZE))
        for i in range(8):
            if data & 1<<i == 1<<i:
                surface.fill(PIXELON, rect=(0,i*BOXSIZE,BOXSIZE,BOXSIZE))
            else:
                surface.fill(PIXELOFF, rect=(0,i*BOXSIZE,BOXSIZE,BOXSIZE))
        page_col["COL"]+=1
        self.screen.blit(surface, self.get_pos(page_col["COL"], page_col["PAGE"]*8))
        if page_col["COL"]+2 == BOARDWIDTH:
            page_col["PAGE"]+=1
            page_col["COL"]=0
        if page_col["PAGE"] >= 8:
            return

    def reset_cursor(self):
        page_col["PAGE"] = 0
        page_col["COL"] = 0


    def set_page_address(self, page):
        page_col["PAGE"] = page 

    def set_column_address(self, col):
        page_col["COL"] = col
