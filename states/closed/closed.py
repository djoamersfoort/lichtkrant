from time import sleep
import sys
from PIL import Image, ImageDraw, ImageFont

# shutdown after 1 minute
# os.system("shutdown 1")

# shutdown text
font = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"
background = "black"

text = "Doei :("

image = Image.new("RGB", (96, 32), "black")
font = ImageFont.truetype(font, size=20)

draw = ImageDraw.Draw(image)
draw.text((48, 16), text, fill="red", anchor="mm", font=font)

while True:
    [sys.stdout.buffer.write(bytes(a)) for a in image.getdata()]
    sleep(0.05)
