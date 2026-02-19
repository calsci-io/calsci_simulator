import random, pygame, sys
from pygame.locals import *

from display.characters import Characters
from ui import DISPLAY_TOP_MARGIN, DISPLAY_SIDE_PADDING, present, scale_value

FPS = 60 # frames per second, the general speed of the program
BASE_BOXSIZE = 3 # size of box height & width in pixels (base scale)
BASE_GAPSIZE = 0 # size of gap between boxes in pixels (base scale)
BOARDWIDTH = 128 # number of columns of icons
BOARDHEIGHT = 64 # number of rows of icons
WINDOWWIDTH = BOARDWIDTH*(BASE_BOXSIZE+BASE_GAPSIZE) # base window width in pixels
WINDOWHEIGHT = BOARDHEIGHT*(BASE_BOXSIZE+BASE_GAPSIZE) # base window height in pixels

PIXELON=(20, 30, 36)
PIXELOFF=(180, 210, 222)

FPSCLOCK = pygame.time.Clock()

page_col={"PAGE":0,
          "COL":0}

def get_display_metrics(screen):
    box = scale_value(BASE_BOXSIZE, screen, min_value=1)
    gap = scale_value(BASE_GAPSIZE, screen, min_value=0)
    display_w = BOARDWIDTH * (box + gap)
    display_h = BOARDHEIGHT * (box + gap)
    return box, gap, display_w, display_h


class Display:
    def __init__(self, screen, chrs):
        self.screen = screen
        self.chrs = chrs
        self.update_layout()

    def update_layout(self):
        self.boxsize, self.gapsize, display_w, display_h = get_display_metrics(self.screen)
        side_padding = scale_value(DISPLAY_SIDE_PADDING, self.screen, min_value=0)
        top_margin = scale_value(DISPLAY_TOP_MARGIN, self.screen, min_value=0)
        self.xmargin = max((self.screen.get_width() - display_w) // 2, side_padding)
        self.ymargin = top_margin

    
    def draw_pixel(self,posx, posy, size, color):
        pygame.draw.rect(self.screen, color, (posx, posy, size, size))

    def clear_display(self):
        self.turn_off_all_pixels()
        present()

    def turn_off_all_pixels(self):
        for i in range(BOARDWIDTH):
            for j in range(BOARDHEIGHT):
                self.draw_pixel(
                    posx=i * (self.boxsize + self.gapsize) + self.xmargin,
                    posy=j * (self.boxsize + self.gapsize) + self.ymargin,
                    size=self.boxsize,
                    color=PIXELOFF,
                )
                # print("drawing pixel: ", (i,j))
        
        present()

    def turn_on_all_pixels(self):
        for i in range(BOARDWIDTH):
            for j in range(BOARDHEIGHT):
                self.draw_pixel(
                    posx=i * (self.boxsize + self.gapsize) + self.xmargin,
                    posy=j * (self.boxsize + self.gapsize) + self.ymargin,
                    size=self.boxsize,
                    color=PIXELON,
                )
                # print("drawing pixel: ", (i,j))

    def turn_on_pixel(self,x, y):
        self.draw_pixel(
            posx=x * (self.boxsize + self.gapsize) + self.xmargin,
            posy=y * (self.boxsize + self.gapsize) + self.ymargin,
            size=self.boxsize,
            color=PIXELON,
        )


    def turn_off_pixel(self,x, y):
        self.draw_pixel(
            posx=x * (self.boxsize + self.gapsize) + self.xmargin,
            posy=y * (self.boxsize + self.gapsize) + self.ymargin,
            size=self.boxsize,
            color=PIXELOFF,
        )

    def get_pos(self,x,y):
        return (x * (self.boxsize + self.gapsize) + self.xmargin, y * (self.boxsize + self.gapsize) + self.ymargin)

    def write_data(self,data):
        if page_col["PAGE"] >= 8:
            return
        # data_queue.put((data, self.get_pos(page_col["COL"], page_col["PAGE"]*8)))
        surface = pygame.Surface((1 * self.boxsize, 8 * self.boxsize))
        for i in range(8):
            if data & 1<<i == 1<<i:
                surface.fill(PIXELON, rect=(0, i * self.boxsize, self.boxsize, self.boxsize))
            else:
                surface.fill(PIXELOFF, rect=(0, i * self.boxsize, self.boxsize, self.boxsize))
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

    def graphics(self, framebuffer):
        """Display a framebuffer on the screen."""
        if not hasattr(framebuffer, 'buffer') or not hasattr(framebuffer, 'width') or not hasattr(framebuffer, 'height'):
            return

        # Clear the display first
        self.turn_off_all_pixels()

        # Convert framebuffer to display
        width = framebuffer.width
        height = framebuffer.height

        # Display each pixel from the framebuffer
        for x in range(min(width, BOARDWIDTH)):
            for y in range(min(height, BOARDHEIGHT)):
                # Get pixel state from framebuffer
                try:
                    pixel_state = framebuffer.pixel(x, y)
                    if pixel_state:
                        self.turn_on_pixel(x, y)
                except:
                    pass

        present()
