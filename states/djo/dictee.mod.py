from PIL import Image, ImageFont, ImageDraw

from states.base import BaseState

import asyncio
import httpx


class State(BaseState):
    # module information
    name = "dictee"
    index = 7
    delay = 30

    dictee_font = "./static/fonts/Montserrat-Medium.ttf"
    dictee_font_bold = "./static/fonts/Montserrat-BoldItalic.ttf"
    show_time = 7  # time every result is displayed on-screen, including slide animation
    results = []
    elapsed = 0

    # get dictee data
    async def get_results(self):
        try:
            response = await self.client.get("https://dictee.djoleden.nl/api/v1/lichtkrant", timeout=5)
        except httpx.RequestError:
            return []
        return response.json()

    async def check(self, _state):
        self.results = await self.get_results()
        return len(self.results) > 0

    async def run(self):
        scroll_x = 0
        fonts = {
            "font9": ImageFont.truetype(self.dictee_font, size=9),
            "font11": ImageFont.truetype(self.dictee_font, size=11),
            "font16": ImageFont.truetype(self.dictee_font_bold, size=16)
        }

        while not self.killed:
            image = Image.new("RGB", (96, 32), "black")
            draw = ImageDraw.Draw(image)
            draw.rectangle([(0, 0), (96, 9)], fill=(7, 40, 50))
            draw.text((48, 1), "UITSLAG DICTEE", fill="white", anchor="mt", font=fonts["font11"])
            for i, res in enumerate(self.results):
                draw.text((2 + i * 96 - scroll_x, 11), res["name"], fill="white", anchor="lt", font=fonts["font11"])
                draw.text((2 + i * 96 - scroll_x, 22), f"{res['score']} / {res['total']}",
                    fill=(200, 200, 200), anchor="lt", font=fonts["font9"])

                grade_color = "lime" if res["passed"] else "red"
                draw.text((93 + i * 96 - scroll_x, 20), str(res["grade"]),
                    fill=grade_color, anchor="rm", font=fonts["font16"])

            await self.output_image(image)
            self.elapsed += 0.1
            if self.elapsed % self.show_time >= (self.show_time - 1) and len(self.results) > 1:
                # round() to prevent addition glitches
                scroll_x = round(scroll_x + (96 / 10), 1)
                if scroll_x >= len(self.results) * 96:
                    scroll_x = 0

            await asyncio.sleep(0.1)
