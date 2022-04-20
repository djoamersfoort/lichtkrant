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
    check_elapsed = 0
    
    @staticmethod
    def get_response():
        try:
            response = requests.get("https://api.nm-games.eu/djo")
        except requests.RequestException:
            return {}
        if not response.ok:
            return {}
        response = response.json()
        return response["djo"] # dict of keer gegamed per player

    # module check function
    def check(self, _state):
        self.check_elapsed += 1
        if self.check_elapsed % 15 != 0:
            return False

        game_status = self.get_response()
        if len(game_status) == 0: return False
            
        now = datetime.now()

        if now.weekday() == 4:  # friday
            return now.hour < 21 or (now.hour == 21 and now.minute < 30)
        elif now.weekday() == 5:  # saturday
            return now.hour < 13

        return False

    def run(self):
        scroll_y = 0
        font_path = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"
        font8 = ImageFont.truetype(font_path, size=8)
        font10 = ImageFont.truetype(font_path, size=10)

        while not self.killed:
            if self.elapsed % 5 == 0: game_status = self.get_response()
        
            image = Image.new("RGB", (96, 32), (0, 0, 50))
            draw = ImageDraw.Draw(image)

            draw.text((48, 11 - scroll_y), "N&M GAMES", fill=(30, 160, 230), anchor="mb", font=font10)
            draw.text((48, 22 - scroll_y), "GAMERS LIST", fill=(230, 30, 230), anchor="mb", font=font10)
            for i, user in enumerate(game_status):
                count = game_status[user]
                if count == 0: continue # show no gamers with 0

                draw.text((2, (i * 8 + 32) - scroll_y), user, fill="white", anchor="lm", font=font8)
                draw.text((94, (i * 8 + 32) - scroll_y), "x" + str(count), fill=(0, 110, 210), anchor="rm", font=font8)

            self.output_image(image)
            sleep(1)
            self.elapsed += 1
            scroll_y += len(game_status)
