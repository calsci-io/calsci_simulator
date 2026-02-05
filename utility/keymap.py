from utility.constants import KeyButtons as KB, KeypadMode as KM

class Keypad:
    def __init__(self, state=KM.DEFAULT):
        keypad_layout_default = [
            [KB.ON, KB.ALPHA, KB.BETA, KB.HOME, KB.WIFI],
            [KB.BACKLIGHT, KB.BACK, KB.TOOLBOX, KB.DIFF, KB.LN],
            [KB.NAV_L, KB.NAV_D, KB.NAV_R, KB.OK, KB.NAV_U],
            [KB.MODULE, KB.BLUETOOTH, KB.SIN, KB.COS, KB.TAN],
            [KB.INGN, KB.PI, KB.EULER_CONSTANT, KB.SUMMATION, KB.FRACTION],
            [KB.LOG, KB.POW, KB.SQRT, KB.POW_2, KB.S_D],
            [KB.SEVEN, KB.EIGHT, KB.NINE, KB.BACKSPACE, KB.ALL_CLEAR],
            [KB.FOUR, KB.FIVE, KB.SIX, KB.MULTIPLY, KB.DIVIDE],
            [KB.ONE, KB.TWO, KB.THREE, KB.PLUS, KB.MINUS],
            [KB.DECIMAL, KB.ZERO, KB.COMMA, KB.ANSWER, KB.EXE],
        ]

        keypad_layout_alpha = [
            [KB.ON, KB.ALPHA, KB.BETA, KB.HOME, KB.WIFI],
            [KB.BACKLIGHT, KB.BACK, KB.CAPS, KB.F, KB.L],
            [KB.NAV_L, KB.NAV_D, KB.NAV_R, KB.OK, KB.NAV_U],
            [KB.A, KB.B, KB.C, KB.D, KB.E],
            [KB.G, KB.H, KB.I, KB.J, KB.K],
            [KB.M, KB.N, KB.O, KB.P, KB.Q],
            [KB.R, KB.S, KB.T, KB.BACKSPACE, KB.ALL_CLEAR],
            [KB.U, KB.V, KB.W, KB.MULTIPLY, KB.DIVIDE],
            [KB.X, KB.Y, KB.Z, KB.PLUS, KB.MINUS],
            [KB.SPACE, KB.OFF, KB.TAB, KB.ANSWER, KB.EXE],  # Add SPACE to KeyButtons enum
        ]

        keypad_layout_beta = [
            [KB.ON, KB.ALPHA, KB.BETA, KB.HOME, KB.WIFI],
            [KB.BACKLIGHT, KB.BACK, KB.UNDO, KB.EQUAL, KB.DOLLAR],
            [KB.NAV_L, KB.NAV_D, KB.NAV_R, KB.OK, KB.NAV_U],
            [KB.COPY, KB.PASTE, KB.ASIN, KB.ACOS, KB.ATAN],
            [KB.AND, KB.BACKTICK, KB.ESCAPED_QUOTE, KB.SINGLE_QUOTE, KB.SHOT],
            [KB.CARET, KB.TILDE, KB.EXCLAMATION, KB.LESS_THAN, KB.GREATER_THAN],
            [KB.LEFT_BRACKET, KB.RIGHT_BRACKET, KB.PERCENT, KB.BACKSPACE, KB.ALL_CLEAR],
            [KB.LEFT_BRACE, KB.RIGHT_BRACE, KB.COLON, KB.ASTERISK, KB.SLASH],
            [KB.LEFT_PAREN, KB.RIGHT_PAREN, KB.SEMICOLON, KB.PLUS, KB.MINUS],
            [KB.AT, KB.QUESTION, KB.BACKSLASH, KB.ANSWER, KB.EXE],
        ]

        self.state = state
        self.states = {
            KM.DEFAULT: keypad_layout_default,
            KM.ALPHA: keypad_layout_alpha,
            KM.BETA: keypad_layout_beta,
        }

    def key_out(self, col, row):
        return self.states[self.state][row][col]

    def key_change(self, state):
        self.state = state
