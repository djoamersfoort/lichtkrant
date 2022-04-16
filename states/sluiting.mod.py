import requests
from PIL import Image, ImageDraw, ImageFont
from time import sleep
from datetime import datetime
from states.base import BaseState


class State(BaseState):

    # module information
    name = "sluiting"
    index = 9
    delay = 300
    scroll_x = 0
    solar_system = Image.open("./static/planets.png").convert(mode="RGB")

    # requests data
    vol_uri = "http://music.djoamersfoort.nl/api/v1/commands/?cmd=volume&volume=50"

    queue_uri = "http://music.djoamersfoort.nl/api/v1/replaceAndPlay"
    queue_data = {
        "item": {
            "uri": "music-library/INTERNAL/DJO Sluiting.mp3"
        }
    }

    # module check function
    def check(self, _state):
        now = datetime.now()

        if now.weekday() == 4:  # friday
            return now.hour == 21 and now.minute >= 55
        elif now.weekday() == 5:  # saturday
            return now.hour == 13 and 25 <= now.minute < 30

    # start music
    def queue_song(self, index):
        requests.get(self.vol_uri)
        sleep(0.5)
        requests.post(self.queue_uri, json=self.queue_data[index])

    # module runner
    def run(self):
        while not self.killed:
            background = self.solar_system.copy()
            background.paste(background, (-self.scroll_x, 0))
            background.paste(background, (-self.scroll_x + background.width, 0))
            self.output_image(background)
            sleep(1)
            self.scroll_x += 1
            if self.scroll_x >= background.width - 96: self.scroll_x = 0
            