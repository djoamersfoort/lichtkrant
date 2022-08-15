from datetime import timedelta, datetime
from time import sleep

from PIL import Image, ImageDraw, ImageFont, ImageOps

from states.base import BaseState


class State(BaseState):

    # module information
    name = "pauze"
    index = 10
    delay = 15

    # module check function
    def check(self, space_state):
        now = datetime.now()
        return now.weekday() == 5 and now.hour == 11 and 30 <= now.minute < 45

    # module runner
    def run(self):
        # shutdown text
        font_path = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"
        text = "|PAUZE|"

        break_end = datetime.now()
        break_end = break_end.replace(hour=11, minute=45, second=0)

        blink_invert = False

        while not self.killed:
            image = Image.new("RGB", (96, 32), "black")
            font = ImageFont.truetype(font_path, size=20)

            draw = ImageDraw.Draw(image)
            draw.text((48, 3), text, fill="orange", anchor="mt", font=font)

            diff = break_end - datetime.now()
            diff_sec = 0

            if diff.days == 0:
                diff_sec = diff.seconds

            date_text = str(timedelta(seconds=diff_sec))

            font = ImageFont.truetype(font_path, size=12)
            draw.text((48, 29), date_text, fill="yellow", anchor="mb", font=font)

            if diff_sec == 0:
                if blink_invert:
                    image = ImageOps.invert(image)

                blink_invert = not blink_invert

            self.output_image(image)
            sleep(0.5)
