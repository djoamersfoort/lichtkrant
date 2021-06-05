import threading
import socket
from random import choice
import math

from states.base import BaseState


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
        self.p1 = Player(x=1, y=int((h / 2) - Player.height / 2), limit=h - 1)
        self.p2 = Player(x=w - 2, y=int((h / 2) - Player.height / 2), limit=h - 1)
        self.ball = Ball(self.dims)
        # TODO wait with moving the ball till there are two players

    def update(self):
        self.p1.move()
        self.p2.move()
        self.ball.move()
        # update scoring
        if self.ball.x < 0:
            self.p2.score += 1
            self.ball.reset("left")
        elif round(self.ball.x) == self.dims["width"] - 1:
            self.p1.score += 1
            self.ball.reset("right")
        # check winner
        # TODO check for 11 points and 2 points diff
        # bounce on the players
        if round(self.ball.x) == 1:
            # TODO bounce back and increase velocity
            pass
        elif round(self.ball.x) == self.dims['width'] - 2:
            # TODO bounce back and increase velocity
            pass


class Player:
    height = 6
    def __init__(self, x, y, limit):
        self.x = x
        self.y = y
        self.score = 0
        self.limit = limit
        self.ishuman = False
        self.movement = 0

    def move(self):
        self.y += self.movement
        self.y = min(max(0, self.y), self.limit - self.height + 1)


class Ball:
    def __init__(self, bounds):
        self.velocity = 1
        self.bounds = bounds
        self.reset()

    def move(self):
        self.x += math.sin(math.radians(self.direction)) * self.velocity
        self.y += math.cos(math.radians(self.direction)) * self.velocity
        if round(self.y) <= 0:
            if self.direction < 90:
                self.direction -= 90
            elif self.direction > 90:
                self.direction += 90
        if round(self.y) >= self.bounds['height'] - 1:
            if self.direction < 180:
                self.direction -= 90
            elif self.direction > 180:
                self.direction -= 90

    def reset(self, direction=None):
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

    white = [255, 255, 255]
    blue = [0, 0, 255]
    red = [255, 0, 0]
    green = [0, 255, 0]

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
                        if player.ishuman:
                            pixels[y][player.x] = self.blue
                        else:
                            pixels[y][player.x] = self.white
                ball = self.game.ball
                ball_x = min(max(0, ball.x), self.game.dims['width'])
                ball_y = min(max(0, ball.y), self.game.dims['height'] - 1)
                pixels[round(ball_y)][round(ball_x)] = self.white
                for y in range(0, self.winh):
                    if y % 2 == 0:
                        pixels[y][int(self.winw / 2)] = self.white
                score_left_x = round(self.game.dims['width'] / 4) - 1
                for y, row in enumerate(number(self.game.p1.score)):
                    for x, pixel in enumerate(row):
                        if pixel:
                            pixels[y + 1][score_left_x + x] = self.white
                score_right_x = round(self.game.dims['width'] / 4 * 3) - 1
                for y, row in enumerate(number(self.game.p2.score)):
                    for x, pixel in enumerate(row):
                        if pixel:
                            pixels[y + 1][score_right_x + x] = self.white
                # flatten, convert and write buffer to display
                self.output_frame(bytes(flatten(pixels)))

    def receive(self):
        HOST = '0.0.0.0'  # Standard loopback interface address (localhost)
        PORT = 9999  # Port to listen on (non-privileged ports are > 1023)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            s.bind((HOST, PORT))
            s.listen()
            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.handleclient,
                                 args=(conn, addr)).start()

    def handleclient(self, conn, addr):
        player = None
        while not self.killed:
            try:
                data = conn.recv(1)
            except Exception:
                if player == '1':
                    self.game.p1.ishuman = False
                if player == '2':
                    self.game.p2.ishuman = False
                break
            if data.decode() == "":
                msg = "redUnknown"
            else:
                if not self.game:
                    self.game = Game({"width": self.winw, "height": self.winh})

                if player is None:
                    if data.decode() == '1' or data.decode() == '2':
                        if data.decode() == '1':
                            if self.game.p1.ishuman:
                                msg = "redSomeone is already player 1"
                            else:
                                self.game.p1.ishuman = True
                                msg = "yellowYou are player 1"
                                player = "1"
                        if data.decode() == '2':
                            if self.game.p2.ishuman:
                                msg = "redSomeone is already player 2"
                            else:
                                self.game.p2.ishuman = True
                                msg = "yellowYou are player 2"
                                player = "2"
                    else:
                        msg = "redUnknown"

                else:
                    if data.decode() == 'w':
                        msg = "greenup"
                        if player == '1':
                            self.game.p1.movement = -1
                        else:
                            self.game.p2.movement = -1

                    elif data.decode() == 's':
                        if player == '1':
                            self.game.p1.movement = 1
                        else:
                            self.game.p2.movement = 1
                        msg = 'greendown'
                    else:
                        msg = 'redUnknown'

            try:
                conn.send(msg.encode())
            except Exception:
                if player == '1':
                    self.game.p1.ishuman = False
                if player == '2':
                    self.game.p2.ishuman = False
                if not self.game.p1.ishuman and not self.game.p2.ishuman:
                    self.game = None
                break
