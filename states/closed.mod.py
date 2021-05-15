import os
import sys

from time import sleep
from PIL import Image, ImageDraw, ImageFont


# module information
name = "closed"
index = 99
delay = 120


# module check function
def check(state):
    return state['djo'] == "closed"


# module runner
def run(_state):
    # shutdown after 1 minute
    os.system("shutdown 1")

    # shutdown text
    font = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"
    text = "Doei :("

    image = Image.new("RGB", (96, 32), "black")
    font = ImageFont.truetype(font, size=20)

    draw = ImageDraw.Draw(image)
    draw.text((48, 16), text, fill="red", anchor="mm", font=font)

    while True:
        [sys.stdout.buffer.write(bytes(a)) for a in image.getdata()]
        sleep(0.05)
