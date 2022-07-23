from states.base import BaseState
from PIL import Image, ImageFont, ImageDraw
from time import sleep
import requests

class State(BaseState):
    # module information
    name = "dictee"
    index = 7
    delay = 10
    show_time = 7 # time every result is displayed on-screen, including slide animation
    elapsed = check_elapsed = 0

    # get dictee data
    @staticmethod
    def get_results():
        try:
            response = requests.get("https://dictee.djoamersfoort.nl/lichtkrant-api")
        except requests.RequestException:
            return []
        if not response.ok:
            return []
        return response.json()

    def check(self, _state):
        self.check_elapsed += 1
        if self.check_elapsed % 15 != 0: return False

        results = self.get_results()
        return len(results) > 0 and self.elapsed <= len(results) * self.show_time

    def run(self):
        scroll_x = 0
        font_path = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"
        fonts = {
            "font9": ImageFont.truetype(font_path, size=9),
            "font11": ImageFont.truetype(font_path, size=11),
            "font16": ImageFont.truetype(font_path, size=16)
        }

        while not self.killed:
            if self.elapsed % 5 == 0: results = self.get_results()
            image = Image.new("RGB", (96, 32), "black")
            draw = ImageDraw.Draw(image)
            draw.rectangle([(0, 0), (96, 9)], fill=(89, 49, 150))
            draw.text((48, 1), "UITSLAG DICTEE", fill="white", anchor="mt", font=fonts["font11"])
            for i, res in enumerate(results):
                draw.text((2 + i * 96 - scroll_x, 12), res["name"], fill="white", anchor="lt", font=fonts["font11"])
                draw.text((2 + i * 96 - scroll_x, 23), str(res["score"]) + "/" + str(res["total"]), fill=(200, 200, 200), anchor="lt", font=fonts["font9"])
                
                grade = round(res["score"] * 9 / res["total"] + 1, 1)
                grade_color = "lime" if grade >= 5.5 else "red"
                draw.text((93 + i * 96 - scroll_x, 21), str(grade), fill=grade_color, anchor="rm", font=fonts["font16"])

            self.output_image(image)
            self.elapsed += 0.2
            if self.elapsed % self.show_time >= (self.show_time - 1) and len(results) > 1:
                # round() to prevent addition glitches
                scroll_x = round(scroll_x + (96 / 5), 1)
                if scroll_x >= len(results) * 96: scroll_x = 0
        
            sleep(0.2)
