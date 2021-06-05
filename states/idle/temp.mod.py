from time import sleep
from PIL import Image, ImageDraw, ImageFont
from states.base import BaseState


class State(BaseState):

    # module information
    name = "temp"
    index = 0
    delay = 12

    # module check function
    def check(self, state):
        self.state = state
        return state['temperature'] is not None

    # module runner
    def run(self):
        # shutdown text
        font_path = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"

        while not self.killed:
            image = Image.new("RGB", (96, 32), "black")

            temp = round(float(self.state['temperature']), 1)

            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(font_path, size=19)
            draw.text((48, 16), f"{temp} °C", fill="blue", anchor="mm", font=font)

            self.output_image(image)
            sleep(0.5)
