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
    vol_uri = "http://music.djoamersfoort.nl/api/v1/commands/?cmd=volume&volume=50"

    queue_uri = "http://music.djoamersfoort.nl/api/v1/replaceAndPlay"
    queue_data = {
        "item": {
            "uri": "music-library/INTERNAL/Ronny V   Efteling Dance Medley 2.0 (Officiële versie).mp3"
        }
    }

    # module check function
    def check(self, state):
        now = datetime.now()

        if now.weekday() == 4:  # friday
            return now.hour == 21 and 55 <= now.minute == 59
        elif now.weekday() == 5:  # saturday
            return now.hour == 12 and 25 <= now.minute <= 30

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
        requests.get(self.vol_uri)
        sleep(0.5)
        requests.post(self.queue_uri, json=self.queue_data)

    # module runner
    def run(self):
        self.queue_song()
        sequence = self.get_image("static/efteling.gif")

        while not self.killed:
            for image in sequence:
                self.output_image(image)
                sleep(0.05)
