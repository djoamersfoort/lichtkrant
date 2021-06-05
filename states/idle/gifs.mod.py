import random

from PIL import Image
from time import sleep
from states.base import BaseState
import glob


class State(BaseState):

    # module information
    name = "gifs"
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
        gifs = glob.glob('static/*.gif')
        random.shuffle(gifs)
        sequence = self.get_image(gifs[0])

        while not self.killed:
            for image in sequence:
                self.output_image(image)
                sleep(0.05)
