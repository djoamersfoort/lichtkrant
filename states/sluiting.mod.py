import requests
from PIL import Image
from time import sleep
from math import floor
from datetime import datetime
from states.base import BaseState


class State(BaseState):

    # module information
    name = "sluiting"
    index = 9
    delay = 300
    scroll_x = 0
    # planets.png image width MUST be dividable by 96, else module won't work!
    solar_system_fragment_length = floor(Image.open("./static/planets.png").convert(mode="RGB").width / 96)
    solar_systems = [Image.open("./static/planets.png").resize(box=(i * 96, 0, (i + 1) * 96, 32), size=(96, 32)).convert(mode="RGB") for i in range(solar_system_fragment_length)]

    # requests data
    vol_uri = "http://music.djoamersfoort.nl/api/v1/commands/?cmd=volume&volume=50"
    queue_uri = "http://music.djoamersfoort.nl/api/v1/replaceAndPlay"
    queue_data = {"uri": "music-library/INTERNAL/DJO Sluiting.mp3"}

    # module check function
    def check(self, _state):
        now = datetime.now()

        if now.weekday() == 4:  # friday
            return now.hour == 21 and now.minute >= 55
        elif now.weekday() == 5:  # saturday
            return now.hour == 13 and 25 <= now.minute < 30

    # start music
    def queue_song(self):
        requests.get(self.vol_uri)
        sleep(0.5)
        requests.post(self.queue_uri, json=self.queue_data)

    # module runner
    def run(self):
        if self.on_pi:
            try: self.queue_song()
            except: pass

        while not self.killed:
            background = self.solar_system.copy()
            for i, img in enumerate(self.solar_systems):
                background.paste(img, (-self.scroll_x + i * 96, 0))
            background.paste(self.solar_systems[0], (-self.scroll_x + len(self.solar_systems) * 96, 0))
            self.output_image(background)
            sleep(.1)
            self.scroll_x += 1
            if self.scroll_x >= self.solar_system_fragment_length * 96: self.scroll_x = 0
            