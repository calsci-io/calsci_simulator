import st7565 as display


class _DummyForm:
    def __init__(self):
        self.input_list = {}
        self.form_list = []

    def update(self):
        pass

    def update_buffer(self, key):
        pass


class _DummyFormRefresh:
    def refresh(self, state=None):
        return None


class _DummyNav:
    def current_state(self):
        return ""

    def set_restore_callback(self, callback=None):
        return None

    def draw_state(self, state):
        return None


class _DummyTyper:
    class _DummyKeypad:
        def keypad_loop(self, idle_callback=None):
            return None

    def __init__(self):
        self.keypad = self._DummyKeypad()

    def start_typing(self):
        raise RuntimeError("interactive typing not available in staged unit tests")


app = object()
current_app = ["graph", "scientific_calculator"]
form = _DummyForm()
form_refresh = _DummyFormRefresh()
nav = _DummyNav()
typer = _DummyTyper()


def keypad_state_manager(x):
    return None


def keypad_state_manager_reset():
    return None

