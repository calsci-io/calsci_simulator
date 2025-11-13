from components import Button
from constants import KeyButtons as KB, KeypadMode as KM


def get_buttons(screen, state="d"):
    START_POINT = 225
    HEIGHT, WIDTH = 40, 40
    GAP_X, GAP_Y = 10, 10  # control horizontal & vertical spacing globally

    buttons = []

    def create_row(row, start_x, start_y, gap_x):
        """Helper: creates buttons in a row with given gap."""
        return [
            Button(kb, HEIGHT, WIDTH, start_x + i * (WIDTH + gap_x), start_y)
            for i, kb in enumerate(row)
        ]

    # --- Navigation Buttons ---
    nav_buttons = [
        Button(KB.OK, 50, 50, 300, 325),
        Button(KB.NAV_U, 50, 25, 300, 325 - (25 + GAP_Y)),
        Button(KB.NAV_D, 50, 25, 300, 325 + 50 + GAP_Y),
        Button(KB.NAV_L, 40, 50, 300 - (65 + GAP_X // 2), 325),
        Button(KB.NAV_R, 40, 50, 300 + (65 + GAP_X // 2), 325),
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
    section_1_layouts = {
        KM.DEFAULT: [
            [KB.TOOLBOX, KB.MODULE, KB.BLUETOOTH, KB.SIN, KB.COS, KB.TAN],
            [KB.DIFF, KB.INGN, KB.PI, KB.EULER_CONSTANT, KB.SUMMATION, KB.DIVIDE],
            [KB.LN, KB.LOG, KB.POW, KB.SQRT, KB.POW_2, KB.S_D],
        ],
        KM.ALPHA: [
            [KB.CAPS, KB.A, KB.B, KB.C, KB.D, KB.E],
            [KB.F, KB.G, KB.H, KB.I, KB.J, KB.K],
            [KB.L, KB.M, KB.N, KB.O, KB.P, KB.Q],
        ],
        KM.BETA: [
            [KB.UNDO, KB.COPY, KB.PASTE, KB.ASIN, KB.ACOS, KB.ATAN],
            [KB.EQUAL, KB.AND, KB.BACKTICK, KB.ESCAPED_QUOTE, KB.SINGLE_QUOTE, KB.SLASH],
            [KB.DOLLAR, KB.CARET, KB.TILDE, KB.EXCLAMATION, KB.LESS_THAN, KB.GREATER_THAN],
        ],
    }

    section_2_layouts = {
        KM.DEFAULT: [
            [KB.SEVEN, KB.EIGHT, KB.NINE, KB.BACKSPACE, KB.ALL_CLEAR],
            [KB.FOUR, KB.FIVE, KB.SIX, KB.PLUS, KB.SLASH],
            [KB.ONE, KB.TWO, KB.THREE, KB.MULTIPLY, KB.MINUS],
            [KB.DECIMAL, KB.ZERO, KB.COMMA, KB.ANSWER, KB.EXE],
        ],
        KM.ALPHA: [
            [KB.R, KB.S, KB.T, KB.BACKSPACE, KB.ALL_CLEAR],
            [KB.U, KB.V, KB.W, KB.PLUS, KB.SLASH],
            [KB.X, KB.Y, KB.Z, KB.MULTIPLY, KB.MINUS],
            [KB.SPACE, KB.OFF, KB.TAB, KB.ANSWER, KB.EXE],
        ],
        KM.BETA: [
            [KB.LEFT_BRACKET, KB.RIGHT_BRACKET, KB.PERCENT, KB.BACKSPACE, KB.ALL_CLEAR],
            [KB.LEFT_BRACE, KB.RIGHT_BRACE, KB.COLON, KB.PLUS, KB.SLASH],
            [KB.LEFT_BRACE, KB.RIGHT_BRACE, KB.COLON, KB.MULTIPLY, KB.MINUS],
            [KB.AT, KB.QUESTION, KB.ESCAPED_QUOTE, KB.ANSWER, KB.EXE],
        ],
    }

    # --- Section 1 Buttons ---
    section_1_y_start = START_POINT + 4 * (HEIGHT + GAP_Y)  # below system buttons
    for i, row in enumerate(section_1_layouts[state]):
        y = section_1_y_start + i * (HEIGHT + GAP_Y)
        buttons.extend(create_row(row, 50, y, GAP_X))

    # --- Section 2 Buttons ---
    section_2_y_start = section_1_y_start +  3.25 * (HEIGHT + GAP_Y)
    for i, row in enumerate(section_2_layouts[state]):
        y = section_2_y_start + i * (HEIGHT + GAP_Y)
        buttons.extend(create_row(row, 50, y, GAP_X + 20))  # slightly wider layout

    # --- Draw all buttons ---
    for button in buttons:
        button.draw(screen)

    return buttons
