from math import fabs
from time import sleep
from typing import cast

from PIL import Image, ImageDraw, ImageFont

from states.base import BaseState
from states.socket import BasePlayer


class Connection(BasePlayer):
    def __init__(self, sio, sid, game):
        super().__init__(sio, sid, game)
        self.player = None

    def on_press(self, key):
        if not self.player:
            return

        if key == "a":
            self.player.left = True
        elif key == "d":
            self.player.right = True
        elif key == "w":
            self.player.jumping = True

    def on_release(self, key):
        if not self.player:
            return

        if key == "a":
            self.player.left = False
        elif key == "d":
            self.player.right = False
        elif key == "w":
            self.player.jumping = False

    def init(self, color, player):
        self.player = player
        self.set_color(color)

    def on_leave(self):
        self.player.conn = None
        game = cast(State, self.game)
        if not game.game.p1.conn and not game.game.p2.conn:
            self.game.game = None


class Game:
    p1_x = 15
    p2_x = 71
    platform = {"x1": 10, "x2": 86, "height": 17}
    timer = 45
    g = 0.3  # valversnelling
    a = 0.04  # beweegversnelling

    def __init__(self):
        self.p1 = Player(x=self.p1_x)
        self.p2 = Player(x=self.p2_x)
        self.background = Image.open("./static/game_assets/splash/background.gif").convert(mode="RGB")
        self.p1_img = Image.open("./static/game_assets/splash/Karakter1.gif").convert(mode="RGB")
        self.p2_img = Image.open("./static/game_assets/splash/Karakter2.gif").convert(mode="RGB")

    def update(self):
        # connection updating
        if not self.p1.conn or not self.p2.conn:
            return
        if self.p1.has_won or self.p2.has_won:
            sleep(5)
            self.reset()
            return

        # game updating
        if self.timer == 0:
            self.p1.has_won = self.p2.has_won = True

        if self.p1.left and not self.p1.right:  # naar links
            self.p1.vx -= self.a
        elif self.p1.right and not self.p1.left:  # naar rechts
            self.p1.vx += self.a
        else:  # stoppen
            self.p1.vx /= 1.06
        if self.p2.left and not self.p2.right:
            self.p2.vx -= self.a
        elif self.p2.right and not self.p2.left:
            self.p2.vx += self.a
        else:
            self.p2.vx /= 1.06

        if self.p1.jumping and not self.p1.airborne:  # springen
            self.p1.airborne = True
            self.p1.vy = -2.5
        if self.p2.jumping and not self.p2.airborne:
            self.p2.airborne = True
            self.p2.vy = -2.5

        self.p1.x += self.p1.vx
        self.p1.y += self.p1.vy
        self.p1.vy += self.g  # zwaartekracht
        if self.platform["x1"] - self.p1.size < self.p1.x < self.platform["x2"] and self.p1.y > \
                self.platform["height"] - self.p1.size:
            self.p1.y = self.platform["height"] - self.p1.size
            self.p1.airborne = False
            self.p1.vy = 0

        self.p2.x += self.p2.vx
        self.p2.y += self.p2.vy
        self.p2.vy += self.g
        if self.platform["x1"] - self.p2.size < self.p2.x < self.platform["x2"] and self.p2.y > \
                self.platform["height"] - self.p2.size:
            self.p2.y = self.platform["height"] - self.p2.size
            self.p2.airborne = False
            self.p2.vy = 0

        # collission detection
        if self.p1.x < self.p2.x + self.p2.size and self.p1.x + self.p1.size > self.p2.x \
                and self.p1.y < self.p2.y + self.p2.size and self.p1.y + self.p1.size > self.p2.y:
            self.p1.vx /= 1.1
            self.p2.vx /= 1.1
            if self.p1.y == self.p2.y:
                if fabs(self.p1.vx) > fabs(self.p2.vx):
                    if self.p1.x > self.p2.x:
                        self.p2.x = self.p1.x - self.p1.size
                    else:
                        self.p2.x = self.p1.x + self.p1.size
                else:
                    if self.p1.x > self.p2.x:
                        self.p1.x = self.p2.x + self.p2.size
                    else:
                        self.p1.x = self.p2.x - self.p2.size
            else:
                if self.p1.vy > self.p2.vy:
                    if self.p1.y > self.p2.y:
                        self.p1.x = self.p2.x + self.p2.size if self.p1.x > self.p2.x else self.p2.x - self.p2.size
                    else:
                        self.p1.y = self.p2.y - self.p2.size
                        self.p1.vy = 0
                elif self.p1.vy < self.p2.vy:
                    if self.p1.y < self.p2.y:
                        self.p2.x = self.p1.x - self.p1.size if self.p1.x > self.p2.x else self.p1.x + self.p1.size
                    else:
                        self.p2.y = self.p1.y - self.p1.size
                        self.p2.vy = 0

        # grant score when someone fell off
        if self.p1.y > 32 and self.p2.y > 32:
            self.p1.has_won = True
            self.p2.has_won = True
        elif self.p1.y > 32:
            self.p2.has_won = True
            self.p2.score += 1
        elif self.p2.y > 32:
            self.p1.has_won = True
            self.p1.score += 1

    def reset(self):
        self.timer = 45
        self.p1.reset(x=self.p1_x)
        self.p2.reset(x=self.p2_x)


class Player:
    def __init__(self, x):
        self.x = x
        self.y = 8
        self.size = 9
        self.vx = 0
        self.vy = 0
        self.score = 0
        self.conn = None
        self.has_won = False
        self.jumping = False
        self.left = False
        self.right = False
        self.airborne = False

    def reset(self, x):
        self.x = x
        self.y = 8
        self.vx = 0
        self.vy = 0
        self.has_won = False
        self.jumping = False
        self.left = False
        self.right = False
        self.airborne = False


class State(BaseState):
    # module information
    name = "splash"
    index = 90
    delay = 5
    calls = 0
    game = None

    def __init__(self):
        super().__init__()
        self.player_class = Connection

    def add_player(self, player):
        if not self.game:
            self.game = Game()
        if not self.game.p1.conn:
            self.game.p1.conn = player
            player.init("#FFD900", self.game.p1)
        elif not self.game.p2.conn:
            self.game.p2.conn = player
            player.init("#00AE00", self.game.p2)
        else:
            return

    # module check function
    def check(self, _state):
        return self.game

    # module runner
    def run(self):
        font8 = ImageFont.truetype(self.font_path, size=8)
        font12 = ImageFont.truetype(self.font_path, size=12)
        font14 = ImageFont.truetype(self.font_path, size=14)

        while not self.killed:
            if self.game:
                self.game.update()
                currentBackg = self.game.background.copy()

                currentBackg.paste(self.game.p1_img, (int(self.game.p1.x), int(self.game.p1.y)))
                currentBackg.paste(self.game.p2_img, (int(self.game.p2.x), int(self.game.p2.y)))
                draw = ImageDraw.Draw(currentBackg)
                tcolor = "red" if self.game.timer < 10 else "black"
                draw.text((48, 26), str(self.game.timer), fill=tcolor, anchor="mm", font=font8)
                draw.text((22, 26), str(self.game.p1.score), fill=(255, 217, 0), anchor="lm", font=font12)
                draw.text((74, 26), str(self.game.p2.score), fill=(0, 174, 0), anchor="rm", font=font12)
                if self.game.p1.has_won or self.game.p2.has_won:
                    draw.text((48, 3), "ROUND OVER!", fill=(120, 0, 0), anchor="mt", font=font14)
                elif not self.game.p1.conn or not self.game.p2.conn:
                    draw.text((48, 3), "WAITING", fill=(120, 0, 0), anchor="mt", font=font14)
                self.output_image(currentBackg)

                self.calls += 1
                if self.calls % 60 == 0 and self.game.p1.conn and self.game.p2.conn:
                    self.game.timer -= 1

                sleep(.017)
