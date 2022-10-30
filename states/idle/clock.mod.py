from datetime import datetime
from time import sleep

from PIL import Image, ImageDraw, ImageFont

from states.base import BaseState


class State(BaseState):
    # module information
    name = "clock"
    index = 0
    delay = 30

    # module check function
    def check(self, _state):
        return True

    def run(self):
        while not self.killed:
            image = Image.new("RGB", (96, 32), "black")
            time_str = datetime.now().strftime("%H:%M:%S")

            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(self.font_path, size=19)
            draw.text((48, 16), time_str, fill="green", anchor="mm", font=font)

            self.output_image(image)
            sleep(0.5)
