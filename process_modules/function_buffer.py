class FunctionBuffer:
    def __init__(self):
        self.clear()

    def clear(self):
        self.active = False
        self.name = ""
        self.block_start = 0
        self.block_end = 0
        self.arg_start = 0
        self.arg_end = 0

    def set_block(self, name, block_start, block_end, arg_start=None, arg_end=None):
        self.active = True
        self.name = name
        self.block_start = block_start
        self.block_end = block_end
        if arg_start is None:
            arg_start = block_start
        if arg_end is None:
            arg_end = block_end
        self.arg_start = arg_start
        self.arg_end = arg_end

    def selection_range(self):
        if not self.active:
            return None
        return (self.block_start, self.block_end)

    def is_cursor_in_block(self, cursor):
        return self.active and self.block_start <= cursor < self.block_end
