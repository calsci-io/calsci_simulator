from ui import Button, OtherButton, draw_shell, scale_value
from ui import DISPLAY_TOP_MARGIN, DISPLAY_BEZEL_PADDING, KEYPAD_TOP_GAP, SYSTEM_TO_MAIN_GAP
from utility.constants import KeyButtons as KB, KeypadMode as KM
from display.display import get_display_metrics
import pygame


SYSTEM_KEY = 40
SYSTEM_GAP_X = 12
SYSTEM_GAP_Y = 8
NAV_OK = 50
NAV_LR_W = 50
NAV_LR_H = NAV_LR_W
NAV_GAP = 4
NAV_UD_W = NAV_LR_W
NAV_UD_H = NAV_LR_W
NAV_OFFSET_X = -6
NAV_OFFSET_Y = -2

MAIN_KEY = 50
MAIN_GAP_X = 5
MAIN_GAP_Y = 16

def get_buttons(screen, alpha=False, beta=False, caps=False, state="d"):
    draw_shell(screen)

    HEIGHT = scale_value(SYSTEM_KEY, screen, min_value=1)
    WIDTH = HEIGHT
    GAP_X = scale_value(SYSTEM_GAP_X, screen, min_value=1)
    GAP_Y = scale_value(SYSTEM_GAP_Y, screen, min_value=1)  # control horizontal & vertical spacing globally
    _, _, display_w, display_h = get_display_metrics(screen)
    MAIN_AREA_WIDTH = display_w
    screen_w = screen.get_width()
    left_margin = (screen_w - MAIN_AREA_WIDTH) // 2
    display_bottom = scale_value(DISPLAY_TOP_MARGIN, screen, min_value=0) + display_h + scale_value(DISPLAY_BEZEL_PADDING, screen, min_value=0) * 2
    top_start = display_bottom + scale_value(KEYPAD_TOP_GAP, screen, min_value=0)

    buttons = []

    def create_row(row, start_x, start_y, gap_x):
        """Helper: creates buttons in a row with given gap."""
        buttons = []
        for i, kb in enumerate(row):
            enabled = False
            
            value = KB.get_symbol(kb)
            if (kb==KB.ALPHA and alpha) or (kb==KB.BETA and beta) or (kb==KB.CAPS and caps):
                enabled = True 
            if caps and kb in [KB.A, KB.B, KB.C, KB.D, KB.E, KB.F, KB.G, KB.H, KB.I, KB.J, KB.K, KB.L, KB.M, KB.N, KB.O, KB.P, KB.Q, KB.R, KB.S, KB.T, KB.U, KB.V, KB.W, KB.X, KB.Y, KB.Z]:
                value = KB.get_symbol(kb).capitalize()
            
            shape = "circle" if kb in (KB.RST, KB.BT) else "rect"
            buttons.append(Button(value, HEIGHT, WIDTH, start_x + i * (WIDTH + gap_x), start_y, enabled, shape=shape))


        return buttons
    
    system_cols = 3
    system_width = system_cols * WIDTH + (system_cols - 1) * GAP_X

    nav_ok_size = scale_value(NAV_OK, screen, min_value=1)
    nav_lr_w = scale_value(NAV_LR_W, screen, min_value=1)
    nav_lr_h = scale_value(NAV_LR_H, screen, min_value=1)
    nav_gap = scale_value(NAV_GAP, screen, min_value=1)
    nav_ud_w = scale_value(NAV_UD_W, screen, min_value=1)
    nav_ud_h = scale_value(NAV_UD_H, screen, min_value=1)
    nav_width = nav_lr_w + nav_gap + nav_ok_size + nav_gap + nav_lr_w
    nav_height = nav_ud_h + nav_gap + nav_ok_size + nav_gap + nav_ud_h

    top_gap = MAIN_AREA_WIDTH - system_width - nav_width
    top_gap = max(top_gap, GAP_X)
    system_start_x = left_margin
    nav_left_edge = system_start_x + system_width + top_gap + scale_value(NAV_OFFSET_X, screen, min_value=-1000)
    system_block_h = 3 * HEIGHT + 2 * GAP_Y
    system_y_start = top_start
    nav_top_edge = system_y_start + (system_block_h - nav_height) // 2 + scale_value(NAV_OFFSET_Y, screen, min_value=-1000)

    nav_ok_x = nav_left_edge + nav_lr_w + nav_gap
    nav_ok_y = nav_top_edge + nav_ud_h + nav_gap
    nav_ud_x = nav_left_edge + (nav_width - nav_ud_w) // 2
    nav_lr_y = nav_ok_y + (nav_ok_size - nav_lr_h) // 2
    
    # --- Navigation Buttons ---
    nav_buttons = [
        Button(KB.get_symbol(KB.OK), nav_ok_size, nav_ok_size, nav_ok_x, nav_ok_y),
        Button(KB.get_symbol(KB.NAV_U), nav_ud_w, nav_ud_h, nav_ud_x, nav_top_edge),
        Button(KB.get_symbol(KB.NAV_D), nav_ud_w, nav_ud_h, nav_ud_x, nav_ok_y + nav_ok_size + nav_gap),
        Button(KB.get_symbol(KB.NAV_L), nav_lr_w, nav_lr_h, nav_left_edge, nav_lr_y),
        Button(KB.get_symbol(KB.NAV_R), nav_lr_w, nav_lr_h, nav_left_edge + nav_lr_w + nav_gap + nav_ok_size + nav_gap, nav_lr_y),
    ]
    buttons.extend(nav_buttons)

    # --- System Buttons (top-left small grid) ---
    system_rows = [
        [KB.ON, KB.RST, KB.BT],
        [KB.ALPHA, KB.BETA, KB.HOME],
        [KB.BACK, KB.BACKLIGHT, KB.WIFI],
    ]

    for i, row in enumerate(system_rows):
        y = system_y_start + (HEIGHT + GAP_Y) * i
        buttons.extend(create_row(row, system_start_x, y, GAP_X))

    # --- Keyboard Layouts ---
    

    # --- Draw all buttons ---
    for button in buttons:
        button.draw(screen)

    return buttons


def get_other_buttons(screen, alpha=False, beta=False, caps=False, state="d"):
    HEIGHT = scale_value(MAIN_KEY, screen, min_value=1)
    WIDTH = HEIGHT
    GAP_X = scale_value(MAIN_GAP_X, screen, min_value=1)
    GAP_Y = scale_value(MAIN_GAP_Y, screen, min_value=1)  # control horizontal & vertical spacing globally
    _, _, display_w, display_h = get_display_metrics(screen)
    MAIN_AREA_WIDTH = display_w
    screen_w = screen.get_width()
    left_margin = (screen_w - MAIN_AREA_WIDTH) // 2
    display_bottom = scale_value(DISPLAY_TOP_MARGIN, screen, min_value=0) + display_h + scale_value(DISPLAY_BEZEL_PADDING, screen, min_value=0) * 2
    top_start = display_bottom + scale_value(KEYPAD_TOP_GAP, screen, min_value=0)
    buttons = []
    section_1_layouts = [
            [(KB.TOOLBOX,KB.CAPS,KB.UNDO), 
             (KB.MODULE,KB.A,KB.COPY), 
             (KB.BLUETOOTH,KB.B,KB.PASTE), 
             (KB.SIN,KB.C,KB.ASIN),
             (KB.COS,KB.D,KB.ACOS),
             (KB.TAN, KB.E,KB.ATAN)],

            [(KB.DIFF,KB.F, KB.EQUAL), 
             (KB.INGN, KB.G, KB.AND), 
             (KB.PI, KB.H, KB.BACKTICK), 
             (KB.EULER_CONSTANT, KB.I, KB.ESCAPED_QUOTE),
             (KB.SUMMATION, KB.J, KB.SINGLE_QUOTE) , 
             (KB.FRACTION, KB.K, KB.SHOT)],

            [(KB.LN, KB.L, KB.DOLLAR), 
             (KB.LOG,KB.M, KB.CARET), 
             (KB.POW, KB.N, KB.TILDE), 
             (KB.SQRT, KB.O, KB.EXCLAMATION), 
             (KB.POW_2, KB.P, KB.LESS_THAN), 
             (KB.S_D, KB.Q, KB.GREATER_THAN)],
        ]

    section_2_layouts = [
            [(KB.SEVEN, KB.R, KB.LEFT_BRACKET), 
             (KB.EIGHT, KB.S, KB.RIGHT_BRACKET), 
             (KB.NINE, KB.T, KB.PERCENT), 
             (KB.BACKSPACE, "", ""), 
             (KB.ALL_CLEAR, "", "")],
            
            [(KB.FOUR, KB.U, KB.LEFT_BRACE), 
             (KB.FIVE, KB.V, KB.RIGHT_BRACE), 
             (KB.SIX, KB.W, KB.COLON), 
             (KB.MULTIPLY, "", ""), 
             (KB.DIVIDE, "", "")],

            [(KB.ONE, KB.X, KB.LEFT_PAREN), 
             (KB.TWO, KB.Y, KB.RIGHT_PAREN), 
             (KB.THREE, KB.Z, KB.SEMICOLON), 
             (KB.PLUS, "", ""), 
             (KB.MINUS, "", "")],
            
            [(KB.DECIMAL, KB.SPACE, KB.AT), 
             (KB.ZERO, KB.OFF, KB.QUESTION), 
             (KB.COMMA, KB.TAB, KB.BACKSLASH), 
             (KB.ANSWER, "", ""), 
             (KB.EXE, "", "")],
        ]
    
    def create_row(row, start_x, start_y, gap_x):
        """Helper: creates buttons in a row with given gap."""

        buttons = []
        for i, kb in enumerate(row):
            enabled = False
            # print(kb)
            default, alpha, beta = kb
            default = KB.get_symbol(default)
            alpha = KB.get_symbol(alpha)
            beta = KB.get_symbol(beta)
            
            if (kb==KB.ALPHA and alpha) or (kb==KB.BETA and beta) or (kb==KB.CAPS and caps):
                enabled = True 
            if caps:
                alpha = KB.get_symbol(alpha).capitalize()
            
            buttons.append(OtherButton(text=default, alpha_text=alpha, beta_text=beta, height=HEIGHT, width=WIDTH, pos_x=start_x + i * (WIDTH + gap_x), pos_y=start_y, enabled=enabled))


        return buttons


    # --- Section 1 Buttons ---
    section_1_gap_x = max(int((MAIN_AREA_WIDTH - (6 * WIDTH)) / 5), GAP_X)
    system_block_h = 3 * scale_value(SYSTEM_KEY, screen, min_value=1) + 2 * scale_value(SYSTEM_GAP_Y, screen, min_value=1)
    section_1_y_start = top_start + system_block_h + scale_value(SYSTEM_TO_MAIN_GAP, screen, min_value=0)
    for i, row in enumerate(section_1_layouts):
        y = section_1_y_start + i * (HEIGHT + GAP_Y)
        buttons.extend(create_row(row, left_margin, y, section_1_gap_x))

        

    # --- Section 2 Buttons ---
    section_2_y_start = section_1_y_start +  3.0 * (HEIGHT + GAP_Y)
    for i, row in enumerate(section_2_layouts):
        y = section_2_y_start + i * (HEIGHT + GAP_Y)
        section_2_gap_x = max(int((MAIN_AREA_WIDTH - (5 * WIDTH)) / 4), GAP_X + scale_value(20, screen, min_value=0))
        buttons.extend(create_row(row, left_margin, y, section_2_gap_x))


    for button in buttons:
        button.draw(screen, state=state)
    
    return buttons
