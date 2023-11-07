import glob
import random
from asyncio import sleep

from PIL import Image

from states.base import BaseState


class State(BaseState):

    # module information
    name = "gifs"
    index = 0
    delay = 12

    # check function
    async def check(self, _state):
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
    async def run(self):
        gifs = glob.glob('static/gifs/*.gif')
        gif = gifs[random.randint(0, len(gifs) - 1)]
        sequence = self.get_image(gif)

        while not self.killed:
            for image in sequence:
                if self.killed:
                    break

                await self.output_image(image)
                await sleep(image.info['duration'] / 1000)
