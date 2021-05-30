from PIL import Image
from time import sleep
from sys import stdout
from states.base import BaseState


class State(BaseState):

    # module information
    name = "nyan"
    index = 0
    delay = 12

    # check function
    def check(self, _state):
        return True

    def get_image(self, path):
        image = Image.open(path)
        image.resize((96, 32))

        sequence = []

        try:
            while True:
                temp = image.copy()
                sequence.append(temp.convert('RGB'))
                image.seek(len(sequence))
        except EOFError:
            pass

        return sequence

    # module runner
    def run(self):
        sequence = self.get_image('static/nyan.gif')

        while not self.killed:
            for frame in sequence:
                stdout.buffer.write(frame.tobytes())
                sleep(0.05)
