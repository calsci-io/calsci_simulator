class Nav:
    def __init__(self, disp_out, chrs):
        self.state="d"
        self.states={"d":"default", "a":"alpha  ", "b":"beta   "}
        self.disp_out=disp_out
        self.chrs=chrs
        self.caps = False

    def state_change(self, state, caps=False):
        self.caps = caps
        self.state=state

    def current_state(self):
        if self.caps:
            return self.states[self.state].capitalize()
        return self.states[self.state]