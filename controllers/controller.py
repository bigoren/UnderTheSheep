
class Controller:

    def __init__(self):
        self.reg_handlers = []

    def __del__(self):
        for handler in self.reg_handlers:
            handler.cancel()

        #print("in del")
