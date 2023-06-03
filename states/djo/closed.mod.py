import os
from time import sleep
from PIL import Image, ImageDraw, ImageFont
from states.base import BaseState


class State(BaseState):

    # module information
    name = "closed"
    index = 99
    delay = 120

    # module check function
    def check(self, space_state):
        return space_state['djo'] == "closed"

    # module runner
    def run(self):
        # shutdown after 1 minute
        os.system("/sbin/halt")

        # shutdown text
        hal_path = "static/hal.png"
        text = "Goodbye,\nDave."

        image = Image.new("RGB", (96, 32), "black")
        font = ImageFont.truetype(self.font_path, size=13)

        draw = ImageDraw.Draw(image)
        draw.text((34, 16), text, fill="red", anchor="lm", font=font, spacing=-2)

        hal_image = Image.open(hal_path).convert("RGBA")
        image.paste(hal_image, (1, 1))

        while not self.killed:
            self.output_image(image)
            sleep(1)
