from time import sleep
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from states.base import BaseState


class State(BaseState):

    # module information
    name = "pauze"
    index = 10
    delay = 30

    # module check function
    def check(self, state):
        now = datetime.now()
        return now.weekday() == 5 and now.hour == 11 and 30 <= now.minute <= 45

    # module runner
    def run(self):
        # shutdown text
        font_path = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"
        text = "|PAUZE|"

        break_end = datetime.today()
        break_end = break_end.replace(hour=11, minute=45)

        while not self.killed:
            image = Image.new("RGB", (96, 32), "black")
            font = ImageFont.truetype(font_path, size=20)

            draw = ImageDraw.Draw(image)
            draw.text((48, 3), text, fill="orange", anchor="mt", font=font)

            diff = (break_end - datetime.now()).seconds
            date_text = str(timedelta(seconds=diff))

            font = ImageFont.truetype(font_path, size=12)
            draw.text((48, 29), date_text, fill="yellow", anchor="mb", font=font)

            self.output_image(image)
            sleep(0.5)
