from states.base import BaseState
from time import sleep
from PIL import Image, ImageDraw, ImageFont
import socketio


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
        for y, row in enumerate(self.tiles):
            for x, color in enumerate(self.tiles[y]):
                color = self.palette[int(color)]
                draw.point((x, y), (color[0], color[1], color[2]))

    def info(self):
        font_path = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"
        font = ImageFont.truetype(font_path, size=10)
        msg = "Draw on\nplace.sverben.nl"
        draw = ImageDraw.Draw(self.image)
        w, h = draw.textsize(msg)
        draw.text(((self.W - w) / 2, (self.H - h) / 2), msg, fill="black", font=font)
