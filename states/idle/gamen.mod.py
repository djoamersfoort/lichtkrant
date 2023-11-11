from datetime import datetime
from asyncio import sleep

import httpx
from PIL import Image, ImageDraw, ImageFont

from states.base import BaseState


class State(BaseState):
    # module information
    name = "gamen"
    index = 0
    delay = 16
    gamers = {}
    elapsed = 0
    check_elapsed = 0

    async def get_response(self):
        try:
            response = await self.client.get("https://api.nm-games.eu/djo", timeout=5)
        except httpx.RequestError:
            return {}
        if not response.ok:
            return {}
        response = response.json()
        return response["djo"]  # dict of keer gegamed per player

    # module check function
    async def check(self, _state):
        self.check_elapsed += 1
        if self.check_elapsed % 15 == 0:
            self.gamers = await self.get_response()

        if len(self.gamers) == 0:
            return False

        now = datetime.now()

        if now.weekday() == 4:  # friday
            return now.hour < 21 or (now.hour == 21 and now.minute < 30)
        if now.weekday() == 5:  # saturday
            return now.hour < 13

        return False

    async def run(self):
        scroll_y = 0
        font_path = "static/fonts/nm-games-font.ttf"
        font8 = ImageFont.truetype(font_path, size=8)
        font10 = ImageFont.truetype(font_path, size=10)

        while not self.killed:
            image = Image.new("RGB", (96, 32), (0, 0, 50))
            draw = ImageDraw.Draw(image)

            draw.text((48, 11 - scroll_y), "N&M GAMES", fill=(30, 160, 230), anchor="mb", font=font10)
            draw.text((48, 22 - scroll_y), "GAMERS LIST", fill=(230, 30, 230), anchor="mb", font=font10)
            for i, user in enumerate(self.gamers):
                count = self.gamers[user]
                if count == 0:
                    continue  # show no gamers with 0

                draw.text((2, (i * 8 + 32) - scroll_y), user, fill="white", anchor="lm", font=font8)
                draw.text((94, (i * 8 + 32) - scroll_y), "x" + str(count), fill=(0, 110, 210), anchor="rm", font=font8)

            await self.output_image(image)
            await sleep(0.5)
            self.elapsed += 0.5
            scroll_y += len(self.gamers)
