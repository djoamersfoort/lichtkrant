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
    solar_system = Image.open("./static/planets.png").resize(box=(0, 0, 96, 32), size=(96, 32)).convert(mode="RGB")
    solar_system_2 = Image.open("./static/planets.png").resize(box=(96, 0, 192, 32), size=(96, 32)).convert(mode="RGB")
    solar_system_3 = Image.open("./static/planets.png").resize(box=(192, 0, 288, 32), size=(96, 32)).convert(mode="RGB")
    solar_system_4 = Image.open("./static/planets.png").resize(box=(288, 0, 384, 32), size=(96, 32)).convert(mode="RGB")    

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
        if self.on_pi: self.queue_song("item")

        while not self.killed:
            background = self.solar_system.copy()
            background.paste(self.solar_system, (-self.scroll_x, 0))
            background.paste(self.solar_system_2, (-self.scroll_x + 96, 0))
            background.paste(self.solar_system_3, (-self.scroll_x + 192, 0))
            background.paste(self.solar_system_4, (-self.scroll_x + 288, 0))
            background.paste(self.solar_system, (-self.scroll_x + 384, 0))
            self.output_image(background)
            sleep(.1)
            self.scroll_x += 1
            if self.scroll_x >= 384: self.scroll_x = 0
            
