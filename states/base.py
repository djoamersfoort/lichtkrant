from threading import Thread


class BaseState(Thread):
    name = "base"

    def __init__(self):
        super().__init__()
        self.killed = False

    def kill(self):
        self.killed = True
