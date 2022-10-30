from time import sleep

from PIL import Image, ImageDraw, ImageFont

from states.base import BaseState


class State(BaseState):

    # module information
    name = "temp"
    index = 0
    delay = 12

    def __init__(self):
        super().__init__()
        self.state = None

    # module check function
    def check(self, space_state):
        self.state = space_state
        return space_state['temperature'] is not None

    # module runner
    def run(self):
        # shutdown text
        while not self.killed:
            image = Image.new("RGB", (96, 32), "black")

            temp = round(float(self.state['temperature']), 1)

            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(self.font_path, size=19)
            draw.text((48, 16), f"{temp} °C", fill="blue", anchor="mm", font=font)

            self.output_image(image)
            sleep(0.5)
