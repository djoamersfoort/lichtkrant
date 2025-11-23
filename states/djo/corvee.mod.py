import asyncio
from math import floor
from os import environ
from random import randint

import httpx
from PIL import Image, ImageDraw, ImageFont, ImageOps

from states.base import BaseState


class State(BaseState):
    # module information
    name = "corvee"
    index = 8
    delay = 3600

    # get corvee dashboard data
    async def get_names(self) -> dict[str, list[str]]:
        if not self.on_pi:
            # Return fake data
            return {
                "selected": ["Jan", "Henk", "Piet"],
                "present": ["Jan", "Henk", "Piet", "Bert", "Gert"]
            }

        try:
            response = await self.client.get(
                "https://corvee.djoamersfoort.nl/api/v1/selected",
                headers={"Authorization": f"Bearer {environ.get('API_TOKEN')}"},
                timeout=5
            )
        except httpx.RequestError:
            return {}
        return response.json()

    # module check function
    async def check(self, _state):
        names = await self.get_names()
        return "selected" in names and len(names["selected"]) > 0

    # runner function
    # pylint: disable=too-many-branches
    async def run(self):
        elapsed = 0
        names = await self.get_names()
        selected_names = names["selected"]
        colors = [(randint(128, 255), randint(128, 255), randint(128, 255)) for _ in names["present"]]
        scroll_y = 0
        scroll_max_speed = 6
        scroll_speed = scroll_max_speed
        chosen = []
        fonts = {
            "noto8": ImageFont.truetype(self.font_path, size=8),
            "noto11": ImageFont.truetype(self.font_path, size=11),
            "noto20": ImageFont.truetype(self.font_path, size=20)
        }
        await self.beep(2)

        while not self.killed:
            image = Image.new("RGB", (96, 32), (0, 0, 0))
            draw = ImageDraw.Draw(image)

            if elapsed < 4:
                draw.text((3, 2), "CORVEE", fill="white", anchor="lt", font=fonts["noto20"])
                draw.text((92, 29), "tijd!", fill="white", anchor="rb", font=fonts["noto11"])

                if elapsed % 1 < 0.5:
                    image = ImageOps.invert(image)
            elif elapsed < 7:
                draw.text((48, 16), "Wie o wie...", fill="yellow", anchor="mm", font=fonts["noto11"])
            elif elapsed < 10:
                draw.text((48, 16), "...zijn de winnaars\nvan vandaag?", fill="yellow", anchor="mm",
                          font=fonts["noto8"])
            elif elapsed < 13:
                draw.text((48, 16), "We zullen\nhet zien!", fill="yellow", anchor="mm", font=fonts["noto11"])
            elif len(names["selected"]) > 0:
                for i, j in enumerate(names["present"]):
                    draw.text((4, 5 + i * 12 - scroll_y), j, fill=colors[i], anchor="lm", font=fonts["noto11"])
                    draw.text((4, 5 + i * 12 - scroll_y + len(names["present"]) * 12), j, fill=colors[i], anchor="lm",
                              font=fonts["noto11"])
                scroll_y += scroll_speed
                if scroll_y > len(names["present"]) * 12:
                    scroll_y = 1

                draw.rectangle([(0, 10), (95, 22)], fill=None, outline=(0, 128, 255), width=1)

                if scroll_speed > 1 and elapsed % 1 < .017:
                    scroll_speed -= 0.5 if scroll_speed <= 3 else 1
                elif scroll_speed == 1 and (scroll_y + 10) % 12 == 0:
                    center_index = floor((scroll_y + 10) / 12)
                    if center_index == len(names["present"]):
                        center_index = 0

                    centered = names["present"][center_index]
                    if centered in names["selected"]:
                        draw.rectangle([(0, 10), (95, 22)], fill=None, outline=(255, 64, 0), width=1)
                        await self.output_image(image)

                        await asyncio.sleep(5)
                        image = ImageOps.solarize(image, threshold=30)
                        await self.output_image(image)

                        await asyncio.sleep(0.25)
                        image = ImageOps.solarize(image, threshold=-30)
                        await self.output_image(image)

                        names["selected"].remove(centered)
                        chosen.append(centered)
                        elapsed = 15
                        scroll_y = 0
                        scroll_speed = scroll_max_speed
            else:
                for i, name in enumerate(chosen):
                    draw.text((48, 5 + 11 * i), name, fill=colors[i], anchor="mm", font=fonts["noto11"])
                for i in range(0, 6):
                    y = (elapsed + i * 8) % 40
                    draw.rectangle([(1, y - 8), (6, y - 4)], fill="blue")
                    draw.rectangle([(89, y - 8), (94, y - 4)], fill="blue")

            if elapsed > 30:
                elapsed = 15
                new_names = await self.get_names()
                if new_names and new_names["selected"] != selected_names:
                    # Names have been updated
                    chosen = new_names["selected"]

            await self.output_image(image)
            await self.beep(2)
            await asyncio.sleep(.017)
            elapsed += .017
