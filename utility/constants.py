

class KeyButtons:
    
    KEY_MAP = {
    "RST": "RST",
    "BT": "Boot",
    "OK": "OK",
    "ON": "ON",

    "NAV_D": "↓",
    "NAV_U": "↑",
    "NAV_L": "←",
    "NAV_R": "→",

    "BETA": "β",
    "ALPHA": "α",

    "HOME": "⌂",
    "WIFI": "📶",
    "TAB": "tab",
    "BACKLIGHT": "🔆",
    "BACK": "↩",
    "TOOLBOX": "🧰",

    "DIFF(": "d/dx",
    "LN": "ln",
    "MODULE": "|x|",
    "BLUETOOTH": "🅱",

    "SIN(": "sin",
    "COS": "cos",
    "TAN": "tan",

    "ASIN(": "sin⁻¹",
    "ACOS(": "cos⁻¹",
    "ATAN(": "tan⁻¹",

    "INGN(": "∫",
    "PI": "π",
    "EULER_CONSTANT": "e",

    "SUMMATION": "∑",
    "FRACTION": "a⁄b",
    "LOG": "log",

    "POW(": "xʸ",
    "POW( ,0.5)": "√",
    "POW( ,2)": "x²",

    "S_D": "S↔D",

    "SEVEN": "7",
    "EIGHT": "8",
    "NINE": "9",
    "NAV_B": "DEL",
    "AC": "AC",

    "FOUR": "4",
    "FIVE": "5",
    "SIX": "6",
    "MULTIPLY": "*",
    "DIVIDE": "/",

    "ONE": "1",
    "TWO": "2",
    "THREE": "3",
    "PLUS": "+",
    "MINUS": "-",

    "DECIMAL": ".",
    "ZERO": "0",
    

    "ANSWER": "ANS",
    "EXE": "EXE",

    "CAPS": "caps",

    "A": "A", "B": "B", "C": "C", "D": "D", "E": "E", "F": "F",
    "G": "G", "H": "H", "I": "I", "J": "J", "K": "K", "L": "L",
    "M": "M", "N": "N", "O": "O", "P": "P", "Q": "Q", "R": "R",
    "S": "S", "T": "T", "U": "U", "V": "V", "W": "W", "X": "X",
    "Y": "Y", "Z": "Z",

    "OFF": "off",

    
    
    "UNDO": "undo",

    
    
    
    
    
    

    "COPY": "❏",
    "PASTE": "📋",

    
    
    
    

    
    
    
    

    
    
    
    
    
    

    
    
    

    

    "SHOT": "shot",
    "SPACE": " "
    }
    @classmethod
    def get_symbol(cls, char):
        return cls.KEY_MAP.get(char.upper(), char)
    
    @classmethod
    def get_char(cls, symbol):
        cls.create_reverse_key_map()
        # print(cls.REVERSE_KEY_MAP.get(symbol, symbol).lower())
        return cls.REVERSE_KEY_MAP.get(symbol, symbol).lower()

    @classmethod
    def create_reverse_key_map(cls):
        cls.REVERSE_KEY_MAP = {v: k for k, v in cls.KEY_MAP.items()}

    RST="rst"
    BT="bt"
    OK="ok"
    ON="on"
    NAV_D="nav_d"
    NAV_U="nav_u"
    NAV_L="nav_l"
    NAV_R="nav_r"
    BETA="beta"
    ALPHA="alpha"
    HOME="home"
    WIFI="wifi"
    TAB="tab"
    BACKLIGHT="backlight"
    BACK="back"
    TOOLBOX="toolbox" 
    DIFF="diff("
    LN="ln"
    MODULE="module"
    BLUETOOTH="bluetooth"
    SIN="sin("
    COS="cos"
    TAN="tan"
    INGN="ingn("
    PI="pi"
    EULER_CONSTANT="e"
    SUMMATION="summation"
    FRACTION="fraction"
    LOG="log"  
    POW="pow("
    SQRT="pow( ,0.5)"
    POW_2="pow( ,2)"
    S_D="S_D"
    SEVEN="7"
    EIGHT="8"
    NINE="9"
    BACKSPACE="nav_b"
    ALL_CLEAR="AC"
    FOUR="4"
    FIVE="5"
    SIX="6"
    MULTIPLY="*"
    DIVIDE="/"
    ONE="1"
    TWO="2"
    THREE="3"
    PLUS="+"
    MINUS="-"
    DECIMAL="."
    ZERO="0"
    COMMA=","
    ANSWER="ans"
    EXE="exe"
    BACKLIGHT="backlight"
    BACK="back"
    CAPS="caps"
    A="a"
    B="b"
    C="c"
    D="d"
    E="e"
    F="f"
    G="g"
    H="h"
    I="i"
    J="j"
    K="k"
    L="l"
    M="m"
    N="n"
    O="o"
    P="p"
    Q="q"
    R="r"
    S="s"
    T="t"
    U="u"
    V="v"
    W="w"
    X="x"
    Y="y"
    Z="z"
    OFF="off"
    TAB="tab"
    AND="&"
    EQUAL="="
    UNDO="undo" 
    DOLLAR="$"
    PERCENT="%"
    SINGLE_QUOTE="'"
    CARET="^"
    PIPE="|"
    BACKSLASH="\\"
    COPY="copy"
    PASTE="paste"
    ASIN="asin("
    ACOS="acos("
    ATAN="atan("
    CARET="^"
    TILDE="~"
    EXCLAMATION="!"
    LESS_THAN="<"
    GREATER_THAN=">"
    LEFT_BRACKET="["
    RIGHT_BRACKET="]"
    PERCENT="%"
    LEFT_BRACE="{"
    RIGHT_BRACE="}"
    COLON=":"
    ASTERISK="*"
    SLASH="/"
    LEFT_PAREN="("
    RIGHT_PAREN=")"
    SEMICOLON=";"
    PLUS="+"
    MINUS="-"
    AT="@"
    BACKTICK="`"
    QUESTION="?"
    ESCAPED_QUOTE="\"" 
    SHOT="shot"
    SPACE=" "

class KeypadMode:
    DEFAULT="d"
    ALPHA="a"
    BETA="b"
