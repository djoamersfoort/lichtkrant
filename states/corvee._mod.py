from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from time import sleep
from sys import stdout
import math

# module information
name = "corvee"
index = 80
delay = 120


# module check function
def check(_state):
    now = datetime.now()
    return (now.weekday() == 5 and now.hour == 12 and
            now.minute >= 30 and now.minute <= 35)


names = ["jan", "klaas", "piet", "gert", "tjeerd", "johan", "bart"]
size = 25

name_len = len(names) * size

choices = [0, 5, 3]


# runner function
def run(_state):
    font_path = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"
    font = ImageFont.truetype(font_path, size=20)

    def frame(names, y, color="blue"):
        image = Image.new("RGB", (96, 32), "black")
        draw = ImageDraw.Draw(image)

        for i, name in enumerate(names):
            y_pos = (name_len - i * size - y) % name_len

            draw.text(
                (48, y_pos), name, fill=color, anchor="mb", font=font)

        return image

    for i in range(0, 3):
        iter_size = name_len * 4 + size * choices[i]

        for y in range(0, iter_size, 4):
            image = frame(names, y % name_len)
            [stdout.buffer.write(bytes(a)) for a in image.getdata()]
            sleep(0.1 * math.pow(y / iter_size, 4))

        for n in range(0, 10):
            color = "white" if n % 2 == 0 else "blue"
            image = frame(names, y % name_len, color)
            [stdout.buffer.write(bytes(a)) for a in image.getdata()]
            sleep(0.2)

    image = Image.new("RGB", (96, 32), "black")
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(font_path, size=12)

    for i in range(0, 3):
        draw.text(
                (48, i * 10), names[choices[i]],
                fill=["red", "green", "blue"][i], anchor="mt", font=font)

    while True:
        [stdout.buffer.write(bytes(a)) for a in image.getdata()]
        sleep(1)
