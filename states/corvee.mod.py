from PIL import Image, ImageDraw, ImageFont, ImageOps
from time import sleep
from states.base import BaseState
from random import randint
from math import floor
import requests

class State(BaseState):
    # module information
    name = "corvee"
    index = 8
    delay = 3600

    # get corvee dashboard data
    @staticmethod
    def get_names():
        try:
            response = requests.get("https://corvee.djoamersfoort.nl/api/v1/selected")
        except requests.exceptions.RequestException:
            return []
        if not response.ok:
            return []
        return response.json()

    # module check function
    def check(self, _state):
        return len(self.get_names()) > 0

    # runner function
    def run(self):
        elapsed = 0
        blink_invert = False
        names = self.get_names()
        colors = [(randint(128, 255), randint(128, 255), randint(128, 255)) for i in names["present"]]
        scroll_y = 0
        scroll_speed = 8
        font_path = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"
        chosen = []
        fonts = {
            "noto8": ImageFont.truetype(font_path, size=8),
            "noto11": ImageFont.truetype(font_path, size=11),
            "noto20": ImageFont.truetype(font_path, size=20)
        }

        while not self.killed:
            image = Image.new("RGB", (96, 32), (0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            if elapsed < 4:
                draw.text((3, 2), "CORVEE", fill="white", anchor="lt", font=fonts["noto20"])
                draw.text((92, 29), "tijd!", fill="white", anchor="rb", font=fonts["noto11"])

                if elapsed % 0.2 < 0.1:
                    if blink_invert:
                        image = ImageOps.invert(image)
                    blink_invert = not blink_invert
            elif elapsed < 7:
                draw.text((48, 16), "Wie o wie...", fill="yellow", anchor="mm", font=fonts["noto11"])
            elif elapsed < 10:
                draw.text((48, 16), "...zijn de winnaars\nvan vandaag?", fill="yellow", anchor="mm", font=fonts["noto8"])
            elif elapsed < 13:
                draw.text((48, 16), "We zullen\nhet zien!", fill="yellow", anchor="mm", font=fonts["noto11"])
            elif len(names["selected"]) > 0:
                for i, j in enumerate(names["present"]):
                    draw.text((4, 5 + i * 12 - scroll_y), j, fill=colors[i], anchor="lm", font=fonts["noto11"])
                    draw.text((4, 5 + i * 12 - scroll_y + len(names["present"]) * 12), j, fill=colors[i], anchor="lm", font=fonts["noto11"])
                scroll_y += scroll_speed
                if scroll_y > len(names["present"]) * 12: scroll_y = 1

                draw.rectangle([(0, 10), (95, 22)], fill=None, outline="cyan", width=1)

                if scroll_speed > 1 and elapsed % 1 < .05: scroll_speed -= 1
                elif scroll_speed == 1 and (scroll_y + 10) % 12 == 0:
                    center_index = floor((scroll_y + 10) / 12)
                    if center_index == len(names["present"]): center_index = 0

                    centered = names["present"][center_index]
                    if centered in names["selected"]:
                        scroll_speed = 0
                        image = ImageOps.solarize(image, threshold=20)
                        sleep(5)
                        image = ImageOps.solarize(image, threshold=-20)
                        names["selected"].remove(centered)
                        chosen.append(centered)
                        elapsed = 15
                        scroll_y = 0
                        scroll_speed = 8
            else:
                for i in range(len(chosen)):
                    draw.text((48, 5 + 11 * i), chosen[i], fill=colors[i], anchor="mm", font=fonts["noto11"])
                for i in range(0, 6):
                    y = (elapsed + i * 8) % 40
                    draw.rectangle([(1, y - 8), (6, y - 4)], fill="blue")
                    draw.rectangle([(89, y - 8), (94, y - 4)], fill="blue")
      
            self.output_image(image)
            sleep(.05)
            elapsed += .05
