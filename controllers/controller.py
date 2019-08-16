
class Controller:

    def __init__(self):
        self.reg_handlers = []

    def cancel_timers(self):
        for handler in self.reg_handlers:
            handler.cancel()
        self.reg_handlers = []
