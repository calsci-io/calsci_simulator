from components import Button
from constants import KeyButtons as KB, KeypadMode as KM

def get_buttons(screen,state='d'):
    START_POINT = 305    
    buttons = []
    ok_button = Button(KB.OK, 50,50, 450, 425)
    up_button = Button(KB.NAV_U, 50, 25, 450, 405-25) 
    down_button = Button(KB.NAV_D, 50, 25, 450, 525-25) 
    left_button = Button(KB.NAV_L, 40, 50, 385, 450-25) 
    right_button = Button(KB.NAV_R, 40, 50, 525, 450-25) 
    
    HEIGHT=50
    WIDTH=50
    GAP=10

    
    on_button = Button(KB.ON, HEIGHT,WIDTH, 50, START_POINT+50)
    rst_button = Button(KB.RST, HEIGHT, WIDTH, 120, START_POINT+50) 
    boot_button = Button(KB.BT, HEIGHT, WIDTH, 190, START_POINT+50) 


    alpha_button = Button(KB.ALPHA, HEIGHT, WIDTH, 50, START_POINT+HEIGHT+GAP+50)
    beta_button = Button(KB.BETA, HEIGHT, WIDTH, 120, START_POINT+HEIGHT+GAP+50) 
    home_button = Button(KB.HOME, HEIGHT, WIDTH, 190, START_POINT+HEIGHT+GAP+50) 
    
    back_button = Button(KB.BACK, HEIGHT,WIDTH, 50, START_POINT+HEIGHT*2.5+GAP+50)
    light_button = Button(KB.BACKLIGHT, HEIGHT, WIDTH, 120, START_POINT+HEIGHT*2.5+GAP+50) 
    wifi_button = Button(KB.WIFI, HEIGHT, WIDTH, 190, START_POINT+HEIGHT*2.5+GAP+50) 

    keyboard_layout_default = [
        [KB.TOOLBOX, KB.MODULE, KB.BLUETOOTH, KB.SIN, KB.COS, KB.TAN],
        [KB.DIFF, KB.INGN, KB.PI, KB.EULER_CONSTANT, KB.SUMMATION, KB.DIVIDE],
        [KB.LN, KB.LOG, KB.POW,  KB.SQRT, KB.POW_2, KB.S_D],
    ]
    keyboard_layout_alpha = [
        [KB.CAPS, KB.A, KB.B, KB.C, KB.D, KB.E],
        [KB.F, KB.G, KB.H, KB.I, KB.J, KB.K],
        [KB.L, KB.M, KB.N, KB.O, KB.P, KB.Q],
    ]
    keyboard_layout_beta = [
        [KB.UNDO, KB.COPY, KB.PASTE, KB.ASIN, KB.ACOS, KB.ATAN],
    [KB.EQUAL, KB.AND, KB.BACKTICK, KB.ESCAPED_QUOTE, KB.SINGLE_QUOTE, KB.SLASH],
    [KB.DOLLAR, KB.CARET, KB.TILDE, KB.EXCLAMATION, KB.LESS_THAN, KB.GREATER_THAN],
    ]

    keyboard_layout_section_1 = {
       KM.DEFAULT: keyboard_layout_default,
       KM.ALPHA: keyboard_layout_alpha,
       KM.BETA: keyboard_layout_beta
    }

    for i,row in enumerate(keyboard_layout_section_1[state]):
        ADDITION = i*1.5+5
        button_1 = Button(row[0], HEIGHT,WIDTH, 50, START_POINT+HEIGHT*(ADDITION)+GAP)
        button_2 = Button(row[1], HEIGHT, WIDTH, 150, START_POINT+HEIGHT*(ADDITION)+GAP) 
        button_3 = Button(row[2], HEIGHT, WIDTH, 250, START_POINT+HEIGHT*(ADDITION)+GAP) 
        button_4 = Button(row[3], HEIGHT,WIDTH, 350, START_POINT+HEIGHT*(ADDITION)+GAP)
        button_5 = Button(row[4], HEIGHT, WIDTH, 450, START_POINT+HEIGHT*(ADDITION)+GAP) 
        button_6 = Button(row[5], HEIGHT, WIDTH, 550, START_POINT+HEIGHT*(ADDITION)+GAP) 
        buttons.append(button_1)
        buttons.append(button_2)
        buttons.append(button_3)
        buttons.append(button_4)
        buttons.append(button_5)
        buttons.append(button_6)
    
    keyboard_layout_default = [
        [KB.SEVEN, KB.EIGHT, KB.NINE, KB.BACKSPACE, KB.ALL_CLEAR],
        [KB.FOUR, KB.FIVE, KB.SIX, KB.PLUS, KB.SLASH],
        [KB.ONE, KB.TWO, KB.THREE, KB.MULTIPLY, KB.MINUS],
        [KB.DECIMAL, KB.ZERO,KB.COMMA,KB.ANSWER, KB.EXE],
    ]
    keyboard_layout_alpha = [
    [KB.R, KB.S, KB.T, KB.BACKSPACE, KB.ALL_CLEAR],
    [KB.U, KB.V, KB.W, KB.MULTIPLY, KB.MINUS],
    [KB.SPACE, KB.OFF, KB.TAB, KB.ANSWER, KB.EXE],
    ]
    keyboard_layout_beta = [
    [KB.LEFT_BRACKET, KB.RIGHT_BRACKET, KB.PERCENT, KB.BACKSPACE, KB.ALL_CLEAR],
    [KB.LEFT_BRACE, KB.RIGHT_BRACE, KB.COLON, KB.ASTERISK, KB.MINUS],
    [KB.AT, KB.QUESTION, KB.ESCAPED_QUOTE, KB.ANSWER, KB.EXE],
    ]


    
    keyboard_layout_section_2 = {
       KM.DEFAULT: keyboard_layout_default,
       KM.ALPHA: keyboard_layout_alpha,
       KM.BETA: keyboard_layout_beta
    }
    
    for i,row in enumerate(keyboard_layout_section_2[state]):
        ADDITION = i*1.5+9.5
        button_1 = Button(row[0], HEIGHT,WIDTH, 50, START_POINT+HEIGHT*(ADDITION)+GAP)
        button_2 = Button(row[1], HEIGHT, WIDTH, 170, START_POINT+HEIGHT*(ADDITION)+GAP) 
        button_3 = Button(row[2], HEIGHT, WIDTH, 290, START_POINT+HEIGHT*(ADDITION)+GAP) 
        button_4 = Button(row[3], HEIGHT,WIDTH, 410, START_POINT+HEIGHT*(ADDITION)+GAP)
        button_5 = Button(row[4], HEIGHT, WIDTH, 530, START_POINT+HEIGHT*(ADDITION)+GAP) 
        buttons.append(button_1)
        buttons.append(button_2)
        buttons.append(button_3)
        buttons.append(button_4)
        buttons.append(button_5)
    
    buttons.append(back_button)
    buttons.append(light_button)
    buttons.append(wifi_button)
    
    buttons.append(home_button)
    buttons.append(boot_button)
    buttons.append(rst_button)
    buttons.append(on_button)
    buttons.append(alpha_button)
    buttons.append(beta_button)
    buttons.append(ok_button)
    buttons.append(up_button)
    buttons.append(down_button)
    buttons.append(left_button)
    buttons.append(right_button)

    for button in buttons:
        button.draw(screen)

    return buttons