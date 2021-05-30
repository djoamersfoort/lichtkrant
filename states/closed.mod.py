import os
import sys
from time import sleep
from PIL import Image, ImageDraw, ImageFont
from states.base import BaseState


class State(BaseState):

    # module information
    name = "closed"
    index = 99
    delay = 120

    # module check function
    def check(self, state):
        return state['djo'] == "closed"

    # module runner
    def run(self):
        # shutdown after 1 minute
        os.system("shutdown 1")

        # shutdown text
        font = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"
        text = "Doei :("

        image = Image.new("RGB", (96, 32), "black")
        font = ImageFont.truetype(font, size=20)

        draw = ImageDraw.Draw(image)
        draw.text((48, 16), text, fill="red", anchor="mm", font=font)

        while not self.killed:
            sys.stdout.buffer.write(image.tobytes())
            sleep(1)
