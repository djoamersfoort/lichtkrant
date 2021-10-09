import socket
from threading import Thread
from PIL import Image, ImageDraw, ImageFont
from time import sleep
from states.base import BaseState


class Game:
    p1_x = 20
    p2_x = 76
    platform = {"x1": 10, "x2": 86, "height": 17}
    timer = 45
    g = 0.981 # valversnelling
    a = 1.1 # beweegversnelling
    
    def __init__(self):
        self.p1 = Player(x = self.p1_x)
        self.p2 = Player(x = self.p2_x)
        self.background = Image.open("./static/splash_assets/background.gif").convert(mode="RGB")
        self.p1_img = Image.open("./static/splash_assets/Karakter1.gif").convert(mode="RGB")
        self.p2_img = Image.open("./static/splash_assets/Karakter2.gif").convert(mode="RGB")

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

        if self.p1.left and not self.p1.right:
            self.p1.vx -= self.a
        elif self.p1.right and not self.p1.left:
            self.p1.vx += self.a
        else:
            self.p1.vx /= 1.2
        if self.p2.left and not self.p2.right:
            self.p2.vx -= self.a
        elif self.p2.right and not self.p2.left:
            self.p2.vx += self.a
        else:
            self.p2.vx /= 1.2

        if self.p1.jumping and not self.p1.airborne:
            self.p1.airborne = True
            self.p1.vy = -3
        if self.p2.jumping and not self.p2.airborne:
            self.p2.airborne = True
            self.p2.vy = -3

        self.p1.x += self.p1.vx
        self.p1.y += self.p1.vy
        self.p1.vy += self.g
        if self.p1.x - self.p1.size > self.platform["x1"] and self.p1.x < self.platform["x2"] and self.p1.y > self.platform["height"] - self.p1.size:
            self.p1.y = self.platform["height"] - self.p1.size
            self.p1.airborne = False
            self.p1.vy = 0

        self.p2.x += self.p2.vx
        self.p2.y += self.p2.vy
        self.p2.vy += self.g
        if self.p2.x - self.p2.size > self.platform["x1"] and self.p2.x < self.platform["x2"] and self.p2.y > self.platform["height"] - self.p2.size:
            self.p2.y = self.platform["height"] - self.p2.size
            self.p2.airborne = False
            self.p2.vy = 0

        if self.p1.x < self.p2.x + self.p2.size and self.p1.x + self.p1.size > self.p2.x and self.p1.y < self.p2.y + self.p2.size and self.p1.y + self.p1.size > self.p2.y:
            self.p1.vx /= 1.1
            self.p2.vx /= 1.1
            if self.p1.y == self.p2.y:
                if self.p1.vx > self.p2.vx:
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

        if self.p1.y > 30 and self.p2.y > 30:
            self.p1.has_won = self.p2.has_won = True
        elif self.p1.y > 30:
            self.p2.has_won = True
            self.p2.score += 1
        elif self.p2.y > 30:
            self.p1.has_won = True
            self.p1.score += 1


    def reset(self):
        self.timer = 45
        self.p1.reset(x = self.p1_x)
        self.p2.reset(x = self.p2_x)


class Player:
    def __init__(self, x):
        self.x = x
        self.y = 10
        self.size = 9
        self.vx = self.vy = self.score = 0
        self.conn = None
        self.has_won = self.jumping = self.left = self.right = self.airborne = False

    def reset(self, x):
        self.x = x
        self.y = 10
        self.has_won = self.jumping = self.left = self.right = self.airborne = False
    
    def process(self, response):
        self.left = bool(response[0])
        self.right = bool(response[1])
        self.jumping = bool(response[2])


class State(BaseState):
    # module information
    name = "splash"
    index = 90
    delay = 5
    calls = 0
    game = Game()

    # module check function
    def check(self, _state):
        return self.game

    # socket gezeik
    def receive(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            s.bind(("0.0.0.0", 42069))
            s.listen()
            while not self.killed:
                conn, addr = s.accept()
                Thread(target=self.msg, args=(conn, addr)).start()

    def msg(self, conn, _addr):
        while not self.killed:
            data = b''
            try:
                data = conn.recv(3)
                conn.send(b"_")
            except Exception:
                if self.game.p1.conn == conn:
                    self.game.reset()
                    self.game.p1.conn = None
                    self.game.p1.score = self.game.p2.score = 0
                if self.game.p2.conn == conn:
                    self.game.reset()
                    self.game.p2.conn = None
                    self.game.p1.score = self.game.p2.score = 0
                if not self.game.p1.conn and not self.game.p2.conn:
                    self.game = None
                break
            if not self.game:
                self.game = Game()
            if not self.game.p1.conn:
                self.game.p1.conn = conn
            elif not self.game.p2.conn:
                self.game.p2.conn = conn
            request = data.decode().strip()
            if request:
                if self.game.p1.conn == conn:
                    self.game.p1.process(request)
                elif self.game.p2.conn == conn:
                    self.game.p2.process(request)

    # module runner
    def run(self):
        font_path = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"

        while not self.killed:
            if self.game:

                currentBackg = self.game.background.copy()
        
                currentBackg.paste(self.game.p1_img, (int(self.game.p1.x), int(self.game.p1.y)))
                currentBackg.paste(self.game.p2_img, (int(self.game.p2.x), int(self.game.p2.y)))
                draw = ImageDraw.Draw(currentBackg)
                font = ImageFont.truetype(font_path, size=8)
                tcolor = "red" if self.game.timer < 10 else "black"
                draw.text((48, 26), str(self.game.timer), fill=tcolor, anchor="mm", font=font)
                font = ImageFont.truetype(font_path, size=12)
                draw.text((22, 28), str(self.game.p1.score), fill=(255,217,0), anchor="lb", font=font)
                draw.text((74, 28), str(self.game.p1.score), fill=(0,174,0), anchor="rb", font=font)
                if self.game.p1.has_won or self.game.p2.has_won:
                    font = ImageFont.truetype(font_path, size=14)
                    draw.text((48, 3), "ROUND OVER!", fill=(120,0,0), anchor="mt", font=font)
                self.output_image(currentBackg)

                self.calls += 1
                if self.calls % 30 == 0:
                    self.game.timer -= 1
                sleep(.034)
