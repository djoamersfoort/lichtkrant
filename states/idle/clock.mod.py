import sys
from states.base import BaseState
from time import sleep
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


class State(BaseState):
    # module information
    name = "clock"
    index = 0
    delay = 3

    # module check function
    def check(self, _state):
        return True

    def run(self):
        font_path = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"

        while not self.killed:
            image = Image.new("RGB", (96, 32), "black")
            time_str = datetime.now().strftime("%H:%M:%S")

            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(font_path, size=19)
            draw.text((48, 16), time_str, fill="green", anchor="mm", font=font)

            sys.stdout.buffer.write(image.tobytes())
            sleep(0.5)
