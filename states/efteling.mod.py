import requests
from PIL import Image
from time import sleep
from datetime import datetime
from states.base import BaseState


class State(BaseState):

    # module information
    name = "efteling"
    index = 9
    delay = 60

    # requests data
    put_uri = "https://music.bitlair.nl/trollibox/data/player/space/playlist"
    put_data = {
        "position": -1,
        "tracks": [
            "mpd://ak47/Ronny V   Efteling Dance Medley 2.0 (Officiële versie).mp3"
        ]
    }

    del_uri = "https://music.bitlair.nl/trollibox/data/player/space/playlist"
    del_data = {
        "positions": [i for i in range(0, 60)]
    }

    skip_uri = "https://music.bitlair.nl/trollibox/data/player/space/current"
    skip_data = {
        "current": 1,
        "relative": True
    }

    vol_uri = "https://music.bitlair.nl/trollibox/data/player/space/volume"
    vol_data = {
        "volume": 0.55
    }

    # module check function
    def check(self, state):
        now = datetime.now()

        if now.weekday() == 4:  # friday
            return now.hour == 21 and now.minute == 55
        elif now.weekday() == 5:  # saturday
            return now.hour == 13 and now.minute == 25

    # load gif
    def get_image(self, path):
        image = Image.open(path)
        image.resize((96, 32))

        sequence = []

        try:
            while True:
                temp = image.copy()
                sequence.append(temp.convert('RGB'))
                image.seek(len(sequence))
        except EOFError:
            pass

        return sequence

    # queue efteling
    def queue_song(self):
        requests.delete(self.del_uri, json=self.del_data)
        sleep(0.5)
        requests.put(self.put_uri, json=self.put_data)
        sleep(0.5)
        requests.post(self.skip_uri, json=self.skip_data)
        sleep(0.5)
        requests.post(self.vol_uri, json=self.vol_data)

    # module runner
    def run(self):
        self.queue_song()
        sequence = self.get_image("static/efteling.gif")

        while not self.killed:
            for image in sequence:
                self.output_image(image)
                sleep(0.05)
