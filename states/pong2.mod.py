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
        self.reset()

    def reset(self):
        self.ball.reset()
        self.p1.reset()
        self.p2.reset()

    def update(self):
        if not self.p1.ishuman or not self.p2.ishuman:
            return
        if self.p1.has_won or self.p2.has_won:
            sleep(5)
            self.reset()
            return
        self.p1.move()
        self.p2.move()
        self.ball.move()
        # bounce on the players OR assign score and serve again
        if round(self.ball.x) <= 1:
            bounce_pos = self.ball.y - self.p1.y
            if bounce_pos >= 0 and bounce_pos <= self.p1.height:
                steps = self.p1.height + 2
                self.ball.direction = 180 - (bounce_pos + 1) * (180 / steps)
                self.ball.velocity *= 1.1
                return
            else:
                self.p2.score += 1
                self.ball.reset("left")
        elif round(self.ball.x) >= self.dims["width"] - 2:
            bounce_pos = self.ball.y - self.p2.y
            if bounce_pos >= 0 and bounce_pos <= self.p2.height:
                steps = self.p2.height + 2
                self.ball.direction = 180 + ((bounce_pos + 1) * (180 / steps))
                self.ball.velocity *= 1.1
                return
            else:
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
            self.y = min(max(self.y, 0.01), self.bounds["height"] - 1.01)

    def reset(self, side=None):
        self.velocity = 2
        dirs = {"right": list(range(45, 135)), "left": list(range(225, 315))}
        self.direction = choice(dirs.get(side, dirs["left"] + dirs["right"]))
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
                ball = self.game.ball
                ball_x = min(max(0, ball.x), self.game.dims["width"] - 1)
                ball_y = min(max(0, ball.y), self.game.dims["height"] - 1)
                pixels[round(ball_y)][round(ball_x)] = WHITE
                for player in [self.game.p1, self.game.p2]:
                    for y in range(player.y, player.y + player.height):
                        pixels[y][player.x] = player.color()
                for y in range(0, self.winh):
                    if y % 2 == 0:
                        pixels[y][int(self.winw / 2)] = WHITE
                scores = [
                    {
                        "score": list(str(self.game.p1.score)),
                        "color": GREEN if self.game.p1.has_won else WHITE,
                        "center": round(self.game.dims["width"] / 4 - 1)
                    },
                    {
                        "score": list(str(self.game.p2.score)),
                        "color": GREEN if self.game.p2.has_won else WHITE,
                        "center": round((self.game.dims["width"] / 4 * 3) - 1)
                    }
                ]
                for sc in scores:
                    digit_left = len(sc["score"]) * 2
                    for index, digit in enumerate(sc["score"]):
                        for y, row in enumerate(number(digit)):
                            for x, pixel in enumerate(row):
                                if pixel:
                                    pos = sc["center"] - digit_left + x
                                    pos += index * 4
                                    pixels[y + 1][pos] = sc["color"]
                # flatten, convert and write buffer to display
                self.output_frame(bytes(flatten(pixels)))

    def receive(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            s.bind(("0.0.0.0", 9999))
            s.listen()
            while not self.killed:
                conn, addr = s.accept()
                threading.Thread(target=self.msg, args=(conn, addr)).start()

    def msg(self, conn, addr):
        player = None
        while not self.killed:
            data = b''
            if player:
                try:
                    data = conn.recv(1)
                    # It is required to send text to find dead connections,
                    # because 'recv' will happily continue without errors.
                    # We send back some dummy data to detect closed sockets,
                    # because empty strings are not enough or even send at all.
                    # tldr: I kind of hate sockets now >.<
                    conn.send(b"_")
                except Exception:
                    if player == "1":
                        self.game.p1.ishuman = False
                        self.game.reset()
                    if player == "2":
                        self.game.p2.ishuman = False
                        self.game.reset()
                    if not self.game.p1.ishuman and not self.game.p2.ishuman:
                        self.game = None
                    break
            if not self.game:
                self.game = Game({"width": self.winw, "height": self.winh})
            # We strip the data and then check if it contains any data.
            # This is done to reset the movement only when new keys are send.
            # Otherwise no movement would be possible at all,
            # as real messages are frequently followed by an empty message.
            request = data.decode().strip()
            movements = {"w": -1, "s": 1}
            if player == "1" and request:
                self.game.p1.movement = movements.get(request, 0)
            elif player == "2" and request:
                self.game.p2.movement = movements.get(request, 0)
            elif not self.game.p1.ishuman:
                player = "1"
                self.game.p1.ishuman = True
                if self.game.p2.ishuman:
                    self.game.reset()
            elif not self.game.p2.ishuman:
                player = "2"
                self.game.p2.ishuman = True
                if self.game.p1.ishuman:
                    self.game.reset()
