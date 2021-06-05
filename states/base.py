from threading import Thread
from sys import stdout


class BaseState(Thread):
    name = "base"

    def __init__(self):
        super().__init__()
        self.killed = False

    def kill(self):
        self.killed = True

    def output_image(self, pil_image):
        stdout.buffer.write(pil_image.tobytes())

    def output_frame(self, frame):
        stdout.buffer.write(frame)
