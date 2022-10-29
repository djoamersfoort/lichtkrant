from datetime import datetime
from math import floor
from time import sleep

import requests
from PIL import Image

from states.base import BaseState


class State(BaseState):
    # module information
    name = "sluiting"
    index = 9
    delay = 300
    scroll_x = 0
    # planets.png image width MUST be dividable by 96, else module won't work!
    solar_system_fragment_length = floor(Image.open("./static/planets.png").convert(mode="RGB").width / 96)
    solar_systems = [
        Image.open("./static/planets.png").resize(box=(i * 96, 0, (i + 1) * 96, 32), size=(96, 32)).convert(mode="RGB")
        for i in range(solar_system_fragment_length)]

    # requests data
    queue_uri = "http://music.djoamersfoort.nl/mopidy/rpc"
    queue_data = {"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.add",
                  "params": {"uris": ["local:track:nathan/afsluiting.mp3"]}}

    # module check function
    def check(self, _state):
        now = datetime.now()

        if now.weekday() == 4:  # friday
            return now.hour == 21 and now.minute >= 55
        if now.weekday() == 5:  # saturday
            return now.hour == 13 and 25 <= now.minute < 30
        return False

    # start music
    def queue_song(self):
        # get tlid and play sluiting track
        try:
            response = requests.post(self.queue_uri, json=self.queue_data, timeout=5)
            tlid = response.json()["result"][0]["tlid"]
            requests.post(self.queue_uri,
                          json={"jsonrpc": "2.0", "id": 1, "method": "core.playback.play", "params": {"tlid": tlid}},
                          timeout=5)
        except Exception:
            pass

    # module runner
    def run(self):
        if self.on_pi:
            self.queue_song()
        while not self.killed:
            background = self.solar_systems[0].copy()
            for i, img in enumerate(self.solar_systems):
                background.paste(img, (-self.scroll_x + i * 96, 0))
            background.paste(self.solar_systems[0], (-self.scroll_x + len(self.solar_systems) * 96, 0))
            self.output_image(background)
            sleep(.1)
            self.scroll_x += 1
            if self.scroll_x >= self.solar_system_fragment_length * 96:
                self.scroll_x = 0
