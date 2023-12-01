from asyncio import sleep

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

    def __init__(self, stdout):
        super().__init__(stdout)
        self.sio.on("board", self.board)
        self.sio.on("color", self.color)
        self.sio.connect("https://place.djoamersfoort.nl")

    # module check function
    async def check(self, _state):
        return self.tiles is not None and self.palette is not None

    async def run(self):
        self.info()
        while not self.killed:
            if self.time == 10:
                self.draw()
            await self.output_image(self.image)
            self.time += 1
            await sleep(0.5)
        self.time = 0
        self.sio.disconnect()

    def board(self, data):
        self.tiles = data
        self.draw()

    @staticmethod
    def hex_to_rgb(code):
        code = code.lstrip("#")

        return tuple(int(code[i:i + 2], 16) for i in (0, 2, 4))

    def color(self, data):
        self.tiles[data["x"]][data["y"]] = data["color"]
        self.draw()

    def draw(self):
        draw = ImageDraw.Draw(self.image)
        for x, column in enumerate(self.tiles):
            for y, color in enumerate(column):
                draw.point((x, y), self.hex_to_rgb(color))
        if self.time < 10:
            self.info()

    def info(self):
        font = ImageFont.truetype(self.font_path, size=10)
        draw = ImageDraw.Draw(self.image)
        draw.text((self.W / 2, 6), "Draw along on", fill="white", anchor="mt",
            stroke_fill="black", stroke_width=2, font=font)
        draw.text((self.W / 2, 18), "place.sverben.nl", fill="cyan", anchor="mt",
            stroke_fill="black", stroke_width=2, font=font)
