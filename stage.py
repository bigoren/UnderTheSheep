
class Stage:

    def __init__(self, loop):
        self.is_full = False
        self._on_full = None
        self._loop = loop

    def new_reading(self, curr_weight):
        if curr_weight > 240 and not self.is_full:
            self.is_full = True
            if self._on_full:
                self._on_full()

    def register_on_full(self, func):
        self._on_full = func
        if self.is_full:
            self._loop.call_soon(func())
