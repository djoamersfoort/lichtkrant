import json
import math
from datetime import datetime, timedelta
from asyncio import sleep

from PIL import Image, ImageDraw, ImageFont

from states.base import BaseState


class State(BaseState):

    # module information
    name = "weather"
    index = 0
    delay = 12

    url = "https://graphdata.buienradar.nl/2.0/forecast/geo/Rain3Hour?" \
          "lat=52.09&lon=5.12&btc=202105271011&ak=3c4a3037-85e6-4d1e-ad6c-f3f6e4b75f2f"

    # check function
    async def check(self, _state):
        return True

    async def get_data(self):
        req = await self.client.get(self.url, timeout=5)
        data = json.loads(req.text)
        return data['forecasts']

    def get_image(self, data):
        is_rainy = False

        font = ImageFont.truetype(self.font_path, size=10)

        image = Image.new("RGB", (96, 32))
        draw = ImageDraw.Draw(image)

        xinc = math.ceil(96 / len(data))

        oldx = 0
        oldy = 0

        for element in data:
            value = element['value']

            if value > 5:
                is_rainy = True
            # value = randint(0, 100)

            newx = oldx + xinc
            newy = min((value / 100) * 2, 1) * 21

            fill = "green"

            if value > 70:
                fill = "red"
            elif value > 40:
                fill = "orange"

            draw.line([(oldx, 31 - oldy), (newx, 31 - newy)], fill=fill)

            oldx = newx
            oldy = newy

        start_time = datetime.now().strftime("%H:%M")
        draw.text((0, 1), start_time, font=font, fill="grey", anchor="lt")
        end_time = (datetime.now() + timedelta(minutes=30)).strftime("%H:%M")
        draw.text((95, 1), end_time, font=font, fill="grey", anchor="rt")

        rain_text = "REGEN" if is_rainy else "DROOG"
        draw.text((48, 1), rain_text, font=font, fill="white", anchor="mt")

        return image

    # module runner
    async def run(self):
        data = await self.get_data()
        image = self.get_image(data)

        while not self.killed:
            await self.output_image(image)
            await sleep(1)
