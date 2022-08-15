import math
import socket
import threading
from random import choice
from time import sleep, time

from states.base import BaseState

WHITE = [255, 255, 255]
BLUE = [0, 0, 255]
GREEN = [0, 255, 0]
GRAY = [100, 100, 100]


class Game:
    def __init__(self, dims):
        self.dims = dims
        h = self.dims["height"]
        w = self.dims["width"]
        self.players = []
        self.players.append(Player(start_pos=0, bounds=(0, h)))
        self.players.append(Player(start_pos=w - 1, bounds=(0, h)))
        self.players.append(Player(start_pos=0, bounds=(0, 32), orientation="horizontal"))
        self.players.append(Player(start_pos=0, bounds=(32, 64), orientation="horizontal"))
        self.players.append(Player(start_pos=0, bounds=(64, 96), orientation="horizontal"))
        self.players.append(Player(start_pos=h - 1, bounds=(0, 32), orientation="horizontal"))
        self.players.append(Player(start_pos=h - 1, bounds=(32, 64), orientation="horizontal"))
        self.players.append(Player(start_pos=h - 1, bounds=(64, 96), orientation="horizontal"))
        self.ball = Ball(self.dims)
        self.reset()

    def reset(self):
        self.ball.reset()
        for player in self.players:
            player.reset()

    def checkCollision(self, orientation, player_pos):
        for player in self.players:
            if player.orientation != orientation:
                continue
            if orientation == "vertical":
                if player.x != player_pos:
                    continue
                if self.ball.y < player.bounds[0] or self.ball.y > player.bounds[1]:
                    continue
                bounce_pos = self.ball.y - player.y
            else:
                if player.y != player_pos:
                    continue
                if self.ball.x < player.bounds[0] or self.ball.x > player.bounds[1]:
                    continue
                bounce_pos = self.ball.x - player.x

            if not player.ishuman:
                self.ball.direction = 180 - self.ball.direction
                return
            if 0 <= bounce_pos <= player.height:
                steps = player.height + 2
                if player_pos == 0:
                    self.ball.direction = 180 - ((bounce_pos + 1) * (180 / steps))
                else:
                    self.ball.direction = 180 + ((bounce_pos + 1) * (180 / steps))
                self.ball.velocity *= 1.1
                self.ball.last_player = player
                return

        if self.ball.last_player:
            self.ball.last_player.score += 1
        self.ball.reset()

    def update(self):
        if not self.players[0].ishuman or not self.players[1].ishuman:
            return
        for player in self.players:
            if player.has_won:
                sleep(5)
                self.reset()
                return
            player.move()
        self.ball.move()
        # bounce on the players OR assign score and serve again
        if self.ball.x <= 0:
            self.checkCollision("vertical", 0)
        if self.ball.x >= self.dims["width"]:
            self.checkCollision("vertical", self.dims["width"] - 1)
        if self.ball.y <= 0:
            self.checkCollision("horizontal", 0)
        if self.ball.y >= self.dims["height"]:
            self.checkCollision("horizontal", self.dims["height"] - 1)
        # check winner
        for player in self.players:
            if player.score >= 11:
                player.has_won = True


class Player:
    def __init__(self, start_pos, bounds, orientation="vertical"):
        self.orientation = orientation
        self.height = 7
        if self.orientation == "vertical":
            self.x = start_pos
        else:
            self.y = start_pos
        self.bounds = bounds
        self.ishuman = False
        self.reset()
        self.code = BLUE

    def reset(self):
        average = (self.bounds[0] + self.bounds[1]) / 2
        if self.orientation == "vertical":
            self.y = int(average - self.height / 2)
        else:
            self.x = int(average - self.height / 2)
        self.score = 0
        self.has_won = False
        self.movement = 0

    def move(self):
        if self.orientation == "vertical":
            self.y += self.movement
            self.y = min(max(self.bounds[0], self.y), self.bounds[1] - self.height)
        else:
            self.x += self.movement
            self.x = min(max(self.bounds[0], self.x), self.bounds[1] - self.height)

    def color(self):
        if self.has_won:
            return GREEN
        if self.ishuman:
            return self.code
        return WHITE


class Ball:
    def __init__(self, bounds):
        self.y = 0
        self.x = 0
        self.direction = None
        self.velocity = None
        self.last_player = None
        self.bounds = bounds
        self.reset()

    def move(self):
        self.x += math.sin(math.radians(self.direction)) * self.velocity
        self.y += math.cos(math.radians(self.direction)) * self.velocity

    def reset(self, side=None):
        self.velocity = 2
        dirs = {"right": list(range(45, 135)), "left": list(range(225, 315))}
        self.direction = choice(dirs.get(side, dirs["left"] + dirs["right"]))
        self.x = self.bounds["width"] / 2
        self.y = self.bounds["height"] / 2
        self.last_player = None


class State(BaseState):
    name = "pong2"
    index = 7
    delay = 5
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
            if not self.game:
                continue
            if not self.on_pi:
                time_start = time()
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
            for player in self.game.players:
                if not player.ishuman:
                    continue
                if player.orientation == "vertical":
                    for y in range(player.y, player.y + player.height):
                        pixels[y][player.x] = player.color()
                else:
                    for x in range(player.x, player.x + player.height):
                        pixels[player.y][x] = player.color()
            scores = []
            for player in self.game.players:
                if not player.ishuman:
                    continue
                if player.orientation == "vertical":
                    y = int((player.bounds[1] - player.bounds[0]) / 2 + player.bounds[0]) - 3
                    x = 2 if player.x == 0 else self.game.dims["width"] - 5
                else:
                    x = int((player.bounds[1] - player.bounds[0]) / 2 + player.bounds[0]) - 2
                    y = 2 if player.y == 0 else self.game.dims["height"] - 7

                scores.append({
                    "score": str(player.score),
                    "color": GREEN if player.has_won else GRAY,
                    "center": (x, y)
                })
            for sc in scores:
                for y, row in enumerate(self.text(sc["score"])):
                    for x, pixel in enumerate(row):
                        if pixel:
                            pos_x = sc["center"][0] + x
                            pos_y = sc["center"][1] + y
                            pixels[pos_y][pos_x] = sc["color"]
            # flatten, convert and write buffer to display
            self.output_frame(bytes(self.flatten(pixels)))
            if not self.on_pi:
                time_end = time()
                time_delta = time_start - time_end
                sleep(max(0.04 - time_delta, 0))

    def receive(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            s.bind(("0.0.0.0", 9999))
            s.listen()
            while not self.killed:
                conn, addr = s.accept()
                threading.Thread(target=self.msg, args=(conn, addr)).start()

    def move(self, movement):
        move = 0
        if not len(movement) == 2:
            return 0

        if movement[0] == "1":
            move -= 1
        if movement[1] == "1":
            move += 1

        return move

    def color(self, code):
        r, g, b = tuple(int(code[i:i + 2], 16) for i in (0, 2, 4))

        return [r, g, b]

    def msg(self, conn, _addr):
        player = None
        while not self.killed:
            data = b''
            if player:
                try:
                    data = conn.recv(7)
                    # It is required to send text to find dead connections,
                    # because 'recv' will happily continue without errors.
                    # We send back some dummy data to detect closed sockets,
                    # because empty strings are not enough or even send at all.
                    # tldr: I kind of hate sockets now >.<
                    conn.send(b"_")
                except Exception:
                    if player is not None:
                        player.ishuman = False
                        self.game.reset()
                    total_players = 0
                    for player in self.game.players:
                        if player.ishuman:
                            total_players += 1
                    if total_players < 2:
                        self.game = None
                    break
            if not self.game:
                self.game = Game({"width": self.winw, "height": self.winh})
            # We strip the data and then check if it contains any data.
            # This is done to reset the movement only when new keys are send.
            # Otherwise no movement would be possible at all,
            # as real messages are frequently followed by an empty message.
            request = data.decode().strip()
            if player is not None:
                if len(request) == 7 and request.startswith("#"):
                    player.code = self.color(request.split("#")[1])
                player.movement = self.move(request)
            else:
                for p in self.game.players:
                    if not p.ishuman:
                        player = p
                        p.ishuman = True
                        self.game.reset()
                        break
