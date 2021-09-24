from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from time import sleep
from states.base import BaseState
from random import randint
import requests

class State(BaseState):
    # module information
    name = "corvee"
    index = 80
    delay = 60
    elapsed = 0
    flash = False

    colors = [(randint(128, 255), randint(128, 255), randint(128, 255)), (randint(128, 255), randint(128, 255), randint(128, 255)), (randint(128, 255), randint(128, 255), randint(128, 255))]
    
    # get corvee dashboard data
    def get_response(self):
        response = requests.get("https://corvee.djoamersfoort.nl/api/v1/selected").json()
        names = response["selected"]
        return names

    # module check function
    def check(self, _state):
        return len(self.get_response()) > 0

    # runner function
    def run(self):
        names = self.get_response()
        font_path = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"

        while not self.killed:

            self.flash = not self.flash
            if self.elapsed < 3:
                image = Image.new("RGB", (96, 32), (randint(0, 255), randint(0, 255), randint(0, 255)) if self.flash else "black")
            else:
                image = Image.new("RGB", (96, 32), "black")

            draw = ImageDraw.Draw(image)

            if self.elapsed >= 14:
                font = ImageFont.truetype(font_path, size=11)
                for i in range(0, len(names)):
                    draw.text((48, 5 + 11 * i), names[i], fill=self.colors[i], anchor="mm", font=font)
                for i in range(-100, 100):
                    draw.rectangle([(2, 2 + self.elapsed + i * 8), (8, 6 + self.elapsed + i * 8)], fill="blue")
                    draw.rectangle([(88, 2 + self.elapsed + i * 8), (94, 6 + self.elapsed + i * 8)], fill="blue")

            elif self.elapsed >= 13:
                font = ImageFont.truetype(font_path, size=28)
                draw.text((72, 16), "1", fill="red", anchor="mm", font=font)
            elif self.elapsed >= 12:
                font = ImageFont.truetype(font_path, size=28)
                draw.text((48, 16), "2", fill="yellow", anchor="mm", font=font)
            elif self.elapsed >= 11:
                font = ImageFont.truetype(font_path, size=28)
                draw.text((24, 16), "3", fill="green", anchor="mm", font=font)
            elif self.elapsed >= 9:
                font = ImageFont.truetype(font_path, size=10)
                draw.text((48, 16), "...van vandaag\nzijn...", fill="yellow", anchor="mm", font=font)
            elif self.elapsed >= 7:
                font = ImageFont.truetype(font_path, size=10)
                draw.text((48, 16), "...voor het\ncorvee...", fill="yellow", anchor="mm", font=font)
            elif self.elapsed >= 5:
                font = ImageFont.truetype(font_path, size=10)
                draw.text((48, 16), "De grote\nwinnaars...", fill="yellow", anchor="mm", font=font)
            elif self.elapsed >= 3:
                font = ImageFont.truetype(font_path, size=24)
                draw.text((48, 16), "Hallo!", fill="cyan", anchor="mm", font=font)
            self.output_image(image)
            sleep(.1)
            self.elapsed += .1
