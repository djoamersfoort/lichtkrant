import sys
from time import sleep
from PIL import Image, ImageDraw, ImageFont


# module information
name = "temp"
index = 0
delay = 12


# module check function
def check(state):
    return True


# module runner
def run(state):
    # shutdown text
    font_path = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"

    while True:
        image = Image.new("RGB", (96, 32), "black")
        font = ImageFont.truetype(font_path, size=20)

        temp = round(float(state['temperature']), 1)

        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_path, size=19)
        draw.text((48, 16), f"{temp} °C", fill="blue", anchor="mm", font=font)

        [sys.stdout.buffer.write(bytes(a)) for a in image.getdata()]
        sleep(0.05)
