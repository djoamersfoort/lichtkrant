from time import sleep

import socketio
from PIL import Image, ImageDraw, ImageFont

from states.base import BaseState


class State(BaseState):
    # module information
    name = "place"
    index = 0
    delay = 30
    sio = socketio.Client()
    tiles = None
    palette = None
    W, H = (96, 32)
    image = Image.new("RGB", (W, H), "black")
    time = 0

    def __init__(self):
        super().__init__()
        self.sio.on("place", self.place)
        self.sio.on("color", self.color)
        self.sio.connect("https://place.sverben.nl")

    # module check function
    def check(self, _state):
        return self.tiles is not None and self.palette is not None

    def run(self):
        self.info()
        while not self.killed:
            if self.time == 10:
                self.draw()
            self.output_image(self.image)
            self.time += 1
            sleep(0.5)
        self.time = 0
        self.sio.disconnect()

    def place(self, data):
        self.tiles = data["place"]
        self.palette = data["palette"]
        self.draw()

    def color(self, data):
        draw = ImageDraw.Draw(self.image)
        color = self.palette[int(data["color"])]
        draw.point((data["x"], data["y"]), (color[0], color[1], color[2]))
        if self.time < 10:
            self.info()

    def draw(self):
        draw = ImageDraw.Draw(self.image)
        for y, _ in enumerate(self.tiles):
            for x, color in enumerate(self.tiles[y]):
                color = self.palette[int(color)]
                draw.point((x, y), (color[0], color[1], color[2]))

    def info(self):
        font_path = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"
        font = ImageFont.truetype(font_path, size=10)
        draw = ImageDraw.Draw(self.image)
        draw.text((self.W / 2, 6), "Draw along on", fill="white", anchor="mt", stroke_fill="black", stroke_width=2, font=font)
        draw.text((self.W / 2, 18), "place.sverben.nl", fill="cyan", anchor="mt", stroke_fill="black", stroke_width=2, font=font)
        sleep(3)
