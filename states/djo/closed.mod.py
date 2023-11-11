import os
from PIL import Image, ImageDraw, ImageFont
from states.base import BaseState

import asyncio


class State(BaseState):

    # module information
    name = "closed"
    index = 99
    delay = 120

    # module check function
    async def check(self, space_state):
        return space_state['djo'] == "closed"

    # module runner
    async def run(self):
        # shutdown after 1 minute
        os.system("/sbin/halt")

        # shutdown text
        hal_path = "static/hal.png"
        text = "Goodbye,\nDave."

        image = Image.new("RGB", (96, 32), "black")
        font = ImageFont.truetype(self.font_path, size=13)

        draw = ImageDraw.Draw(image)
        draw.text((34, 16), text, fill="red", anchor="lm", font=font, spacing=-2)

        hal_image = Image.open(hal_path).convert("RGBA")
        image.paste(hal_image, (1, 1))

        while not self.killed:
            await self.output_image(image)
            await asyncio.sleep(1)
