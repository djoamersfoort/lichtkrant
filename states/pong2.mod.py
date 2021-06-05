import threading
import socket
from random import choice
from time import sleep
import math

from states.base import BaseState

WHITE = [255, 255, 255]
BLUE = [0, 0, 255]
GREEN = [0, 255, 0]


def number(num):
    numbers = {
        "0": [[1, 1, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 1, 1]],
        "1": [[0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1]],
        "2": [[1, 1, 1], [0, 0, 1], [1, 1, 1], [1, 0, 0], [1, 1, 1]],
        "3": [[1, 1, 1], [0, 0, 1], [1, 1, 1], [0, 0, 1], [1, 1, 1]],
        "4": [[1, 0, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1], [0, 0, 1]],
        "5": [[1, 1, 1], [1, 0, 0], [1, 1, 1], [0, 0, 1], [1, 1, 1]],
        "6": [[1, 1, 1], [1, 0, 0], [1, 1, 1], [1, 0, 1], [1, 1, 1]],
        "7": [[1, 1, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1]],
        "8": [[1, 1, 1], [1, 0, 1], [1, 1, 1], [1, 0, 1], [1, 1, 1]],
        "9": [[1, 1, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1], [1, 1, 1]]
    }
    return numbers.get(str(num), [])


def flatten(s):
    if s == []:
        return s
    if isinstance(s[0], list):
        return flatten(s[0]) + flatten(s[1:])
    return s[:1] + flatten(s[1:])


class Game:
    def __init__(self, dims):
        self.dims = dims
        h = self.dims["height"]
        w = self.dims["width"]
        self.p1 = Player(x=1, limit=h)
        self.p2 = Player(x=w - 2, limit=h)
        self.ball = Ball(self.dims)
        self.start()

    def start(self):
        self.ball.reset()
        self.p1.reset()
        self.p2.reset()

    def update(self):
        if not self.p1.ishuman or not self.p2.ishuman:
            return
        if self.p1.has_won or self.p2.has_won:
            sleep(5)
            self.start()
            return
        self.p1.move()
        self.p2.move()
        self.ball.move()
        # bounce on the players
        if round(self.ball.x) == 1:
            bounce_pos = self.ball.y - self.p1.y
            if bounce_pos >= 0 and bounce_pos <= self.p1.height:
                steps = self.p1.height + 2
                self.ball.direction = (bounce_pos + 1) * (180 / steps)
                self.ball.velocity *= 1.1
                return
        elif round(self.ball.x) == self.dims["width"] - 2:
            bounce_pos = self.ball.y - self.p2.y
            if bounce_pos >= 0 and bounce_pos <= self.p2.height:
                steps = self.p2.height + 2
                self.ball.direction = 360 - ((bounce_pos + 1) * (180 / steps))
                self.ball.velocity *= 1.1
                return
        # assign points, skipped if the ball was bounced above
        if self.ball.x < 0:
            self.p2.score += 1
            self.ball.reset("left")
        elif round(self.ball.x) >= self.dims["width"] - 1:
            self.p1.score += 1
            self.ball.reset("right")
        # check winner
        if self.p1.score >= 11 and self.p1.score - self.p2.score >= 2:
            self.p1.has_won = True
        if self.p2.score >= 11 and self.p2.score - self.p1.score >= 2:
            self.p2.has_won = True


class Player:
    def __init__(self, x, limit):
        self.height = 7
        self.x = x
        self.limit = limit
        self.ishuman = False
        self.reset()

    def reset(self):
        self.y = int((self.limit / 2) - self.height / 2)
        self.score = 0
        self.has_won = False
        self.movement = 0

    def move(self):
        self.y += self.movement
        self.y = min(max(0, self.y), self.limit - self.height)

    def color(self):
        if self.has_won:
            return GREEN
        elif self.ishuman:
            return BLUE
        return WHITE


class Ball:
    def __init__(self, bounds):
        self.bounds = bounds
        self.reset()

    def move(self):
        self.x += math.sin(math.radians(self.direction)) * self.velocity
        self.y += math.cos(math.radians(self.direction)) * self.velocity
        if round(self.y) <= 0 or round(self.y) >= self.bounds["height"] - 1:
            self.direction = 180 - self.direction

    def reset(self, direction=None):
        self.velocity = 1
        directions = {"left": [45, 135], "right": [225, 315]}
        self.direction = choice(directions.get(direction, [45, 135, 225, 315]))
        self.x = self.bounds["width"] / 2
        self.y = self.bounds["height"] / 2


class State(BaseState):
    name = "pong2"
    index = 7
    delay = 30
    game = None

    winw = 96
    winh = 32

    def __init__(self):
        super().__init__()
        threading.Thread(target=self.receive).start()

    def check(self, _state):
        return self.game

    def run(self):
        while not self.killed:
            if self.game:
                self.game.update()
                # create a black empty set of pixels
                pixels = []
                for _ in range(self.winh):
                    pixels.append([])
                    for _ in range(self.winw):
                        pixels[-1].append([0, 0, 0])
                # draw all elements
                for player in [self.game.p1, self.game.p2]:
                    for y in range(player.y, player.y + player.height):
                        pixels[y][player.x] = player.color()
                ball = self.game.ball
                ball_x = min(max(0, ball.x), self.game.dims["width"] - 1)
                ball_y = min(max(0, ball.y), self.game.dims["height"] - 1)
                pixels[round(ball_y)][round(ball_x)] = WHITE
                for y in range(0, self.winh):
                    if y % 2 == 0:
                        pixels[y][int(self.winw / 2)] = WHITE
                score_left_x = round(self.game.dims["width"] / 4) - 1
                for y, row in enumerate(number(self.game.p1.score)):
                    for x, pixel in enumerate(row):
                        if pixel:
                            if self.game.p1.has_won:
                                pixels[y + 1][score_left_x + x] = GREEN
                            else:
                                pixels[y + 1][score_left_x + x] = WHITE
                score_right_x = round(self.game.dims["width"] / 4 * 3) - 1
                for y, row in enumerate(number(self.game.p2.score)):
                    for x, pixel in enumerate(row):
                        if pixel:
                            if self.game.p2.has_won:
                                pixels[y + 1][score_right_x + x] = GREEN
                            else:
                                pixels[y + 1][score_right_x + x] = WHITE
                # flatten, convert and write buffer to display
                self.output_frame(bytes(flatten(pixels)))
                sleep(1 / 30)

    def receive(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            s.bind(("0.0.0.0", 9999))
            s.listen()
            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.msg, args=(conn, addr)).start()

    def msg(self, conn, addr):
        player = None
        while not self.killed:
            try:
                data = conn.recv(1)
            except Exception:
                if player == "1":
                    self.game.p1.ishuman = False
                if player == "2":
                    self.game.p2.ishuman = False
                break
            if data.decode() == "":
                msg = "redUnknown"
            else:
                if not self.game:
                    self.game = Game({"width": self.winw, "height": self.winh})

                if player is None:
                    if data.decode() == "1" or data.decode() == "2":
                        if data.decode() == "1":
                            if self.game.p1.ishuman:
                                msg = "redSomeone is already player 1"
                            else:
                                self.game.p1.ishuman = True
                                msg = "yellowYou are player 1"
                                player = "1"
                                if self.game.p2.ishuman:
                                    self.game.start()
                        if data.decode() == "2":
                            if self.game.p2.ishuman:
                                msg = "redSomeone is already player 2"
                            else:
                                self.game.p2.ishuman = True
                                msg = "yellowYou are player 2"
                                player = "2"
                                if self.game.p1.ishuman:
                                    self.game.start()
                    else:
                        msg = "redUnknown"

                else:
                    if data.decode() == "w":
                        msg = "greenup"
                        if player == "1":
                            self.game.p1.movement = -1
                        else:
                            self.game.p2.movement = -1

                    elif data.decode() == "s":
                        if player == "1":
                            self.game.p1.movement = 1
                        else:
                            self.game.p2.movement = 1
                        msg = "greendown"
                    else:
                        msg = "redUnknown"

            try:
                conn.send(msg.encode())
            except Exception:
                if player == "1":
                    self.game.p1.ishuman = False
                if player == "2":
                    self.game.p2.ishuman = False
                if not self.game.p1.ishuman and not self.game.p2.ishuman:
                    self.game = None
                break
