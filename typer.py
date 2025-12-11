from components import Button, OtherButton
from constants import KeyButtons as KB, KeypadMode as KM
import pygame



def get_buttons(screen, alpha=False, beta=False, caps=False, state="d"):
    START_POINT = 200
    HEIGHT, WIDTH = 40, 40
    GAP_X, GAP_Y = 10, 10  # control horizontal & vertical spacing globally

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
            
            buttons.append(Button(value, HEIGHT, WIDTH, start_x + i * (WIDTH + gap_x), start_y, enabled))


        return buttons
    
    NAV_START_POINT = 300
    
    # --- Navigation Buttons ---
    nav_buttons = [
        Button(KB.get_symbol(KB.OK), 50, 50, NAV_START_POINT, NAV_START_POINT),
        Button(KB.get_symbol(KB.NAV_U), 50, 25, NAV_START_POINT, NAV_START_POINT - (25 + GAP_Y)),
        Button(KB.get_symbol(KB.NAV_D), 50, 25, NAV_START_POINT, NAV_START_POINT + 50 + GAP_Y),
        Button(KB.get_symbol(KB.NAV_L), 40, 50, NAV_START_POINT - (40 + GAP_X // 2), NAV_START_POINT),
        Button(KB.get_symbol(KB.NAV_R), 40, 50, NAV_START_POINT + (50 + GAP_X // 2), NAV_START_POINT),
    ]
    buttons.extend(nav_buttons)

    # --- System Buttons (top-left small grid) ---
    system_rows = [
        [KB.ON, KB.RST, KB.BT],
        [KB.ALPHA, KB.BETA, KB.HOME],
        [KB.BACK, KB.BACKLIGHT, KB.WIFI],
    ]

    for i, row in enumerate(system_rows):
        y = START_POINT + (HEIGHT + GAP_Y) * i + 50
        buttons.extend(create_row(row, 50, y, GAP_X))

    # --- Keyboard Layouts ---
    

    # --- Draw all buttons ---
    for button in buttons:
        button.draw(screen)

    return buttons


def get_other_buttons(screen, alpha=False, beta=False, caps=False, state="d"):
    START_POINT = 140
    HEIGHT, WIDTH = 50, 50
    GAP_X, GAP_Y = 5, 20  # control horizontal & vertical spacing globally
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
             (KB.FRACTION, KB.K, KB.SLASH)],

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
             (KB.PLUS, "", ""), 
             (KB.SLASH, "", "")],

            [(KB.ONE, KB.X, KB.LEFT_PAREN), 
             (KB.TWO, KB.Y, KB.RIGHT_PAREN), 
             (KB.THREE, KB.Z, KB.COLON), 
             (KB.MULTIPLY, "", ""), 
             (KB.MINUS, "", "")],
            
            [(KB.DECIMAL, KB.SPACE, KB.AT), 
             (KB.ZERO, KB.OFF, KB.QUESTION), 
             (KB.COMMA, KB.TAB, KB.ESCAPED_QUOTE), 
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
    section_1_y_start = START_POINT + 4 * (HEIGHT + GAP_Y)  # below system buttons
    for i, row in enumerate(section_1_layouts):
        y = section_1_y_start + i * (HEIGHT + GAP_Y)
        buttons.extend(create_row(row, 50, y, GAP_X))

        

    # --- Section 2 Buttons ---
    section_2_y_start = section_1_y_start +  3.25 * (HEIGHT + GAP_Y)
    for i, row in enumerate(section_2_layouts):
        y = section_2_y_start + i * (HEIGHT + GAP_Y)
        buttons.extend(create_row(row, 50, y, GAP_X + 20))  # slightly wider layout


    for button in buttons:
        button.draw(screen, state=state)
    
    return buttons