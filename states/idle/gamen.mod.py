from states.base import BaseState
from time import sleep
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import requests

class State(BaseState):
    # module information
    name = "gamen"
    index = 0
    delay = 16
    elapsed = 0
    
    # module check function
    def check(self, _state):
        dt = datetime.now()
        if dt.weekday() == 4: # friday
            return dt.hour < 21 or (dt.hour == 21 and dt.minute < 30)
        elif dt.weekday() == 5: # saturday
            return dt.hour < 13

    def run(self):
        font_path = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"
        
        while not self.killed:
            response = requests.get("https://nm-games.eu/media/djo-game-register.json").json()
            keer_gegamed = str(response["keer_gegamed"])
            wall_of_shame = response["wall_of_shame"]

            image = Image.new("RGB", (96, 32), (0, 0, 50))
            draw = ImageDraw.Draw(image)
        
            if self.elapsed < self.delay / 2:
                fsize = 14 if len(keer_gegamed) >= 3 else 18
                font = ImageFont.truetype(font_path, size=fsize)
                draw.text((15, 16), keer_gegamed, fill="white", anchor="mm", font=font)

                font = ImageFont.truetype(font_path, size=8)
                nm_games = "N&M Game" if keer_gegamed == "1" else "N&M Games"
                before_time = "13:00!" if datetime.now().weekday() == 5 else "21:30!"
                draw.text((63, 7), nm_games, fill="white", anchor="mm", font=font)
                draw.text((63, 16), "gespeeld vóór", fill="white", anchor="mm", font=font)
                draw.text((63, 25), before_time, fill="white", anchor="mm", font=font)
            else:
                font = ImageFont.truetype(font_path, size=12)
                draw.text((49, 1), "WALL OF SHAME", fill=(230, 30, 230), anchor="mt", font=font)
                font = ImageFont.truetype(font_path, size=7)
                for i in range(0, len(wall_of_shame)):
                    height = 17 if i % 2 == 0 else 26
                    draw.text(((1 + i * 20) - (self.elapsed - self.delay / 2) * (len(wall_of_shame) - 1), height), wall_of_shame[i], fill="white", anchor="lm", font=font)


            self.output_image(image)
            sleep(1)
            self.elapsed += 1