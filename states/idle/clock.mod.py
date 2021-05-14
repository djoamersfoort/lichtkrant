import sys
from time import sleep
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


# module information
name = "clock"
index = 0
delay = 30


# module check function
def check(state):
    return True


# module runner
def run():
    # shutdown text
    font_path = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"

    while True:
        image = Image.new("RGB", (96, 32), "black")
        font = ImageFont.truetype(font_path, size=20)

        time_str = datetime.now().strftime("%H:%M:%S")

        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_path, size=19)
        draw.text((48, 16), time_str, fill="green", anchor="mm", font=font)

        for _i in range(19):
            [sys.stdout.buffer.write(bytes(a)) for a in image.getdata()]
            sleep(0.05)
