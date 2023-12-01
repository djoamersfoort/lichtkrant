import math
from random import choice
from time import time
from typing import cast

from states.base import BaseState
from states.socket import BasePlayer

from asyncio import sleep

WHITE = [255, 255, 255]
BLUE = [0, 0, 255]
GREEN = [0, 255, 0]
GRAY = [100, 100, 100]


class Game:
    def __init__(self, dims):
        self.dims = dims
        h = self.dims["height"]
        w = self.dims["width"]
        self.paddles = []
        self.paddles.append(Paddle(start_pos=0, bounds=(0, h)))
        self.paddles.append(Paddle(start_pos=w - 1, bounds=(0, h)))
        self.paddles.append(Paddle(start_pos=0, bounds=(0, 32), orientation="horizontal"))
        self.paddles.append(Paddle(start_pos=0, bounds=(32, 64), orientation="horizontal"))
        self.paddles.append(Paddle(start_pos=0, bounds=(64, 96), orientation="horizontal"))
        self.paddles.append(Paddle(start_pos=h - 1, bounds=(0, 32), orientation="horizontal"))
        self.paddles.append(Paddle(start_pos=h - 1, bounds=(32, 64), orientation="horizontal"))
        self.paddles.append(Paddle(start_pos=h - 1, bounds=(64, 96), orientation="horizontal"))
        self.ball = Ball(self.dims)
        self.reset()

    def reset(self):
        self.ball.reset()
        for player in self.paddles:
            player.reset()

    def check_collision(self, orientation, player_pos):
        for player in self.paddles:
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

    async def update(self):
        if not self.paddles[0].ishuman or not self.paddles[1].ishuman:
            return
        for player in self.paddles:
            if player.has_won:
                await sleep(5)
                self.reset()
                return
            player.move()
        self.ball.move()
        # bounce on the players OR assign score and serve again
        if self.ball.x <= 0:
            self.check_collision("vertical", 0)
        if self.ball.x >= self.dims["width"]:
            self.check_collision("vertical", self.dims["width"] - 1)
        if self.ball.y <= 0:
            self.check_collision("horizontal", 0)
        if self.ball.y >= self.dims["height"]:
            self.check_collision("horizontal", self.dims["height"] - 1)
        # check winner
        for player in self.paddles:
            if player.score >= 11:
                player.has_won = True


class Paddle:
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
        self.player = None

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


class Player(BasePlayer):
    def __init__(self, sio, sid, game):
        super().__init__(sio, sid, game)
        self.paddle = None

    def on_press(self, key):
        if key in ('w', 'a'):
            self.paddle.movement = -1
        elif key in ('s', 'd'):
            self.paddle.movement = 1

    def on_release(self, _key):
        self.paddle.movement = 0

    def on_leave(self):
        self.paddle.player = None
        self.paddle.ishuman = False
        total_players = 0
        game = cast(State, self.game)
        for player in game.game.paddles:
            if player.ishuman:
                total_players += 1
        if total_players == 0:
            game.game = None


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

    def __init__(self, stdout):
        super().__init__(stdout)
        self.player_class = Player
        self.game_meta = "static/game_meta/pong2.json"

    async def check(self, _state):
        return self.game

    async def run(self):
        while not self.killed and self.game:
            if not self.on_pi:
                time_start = time()
            await self.game.update()
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
            for player in self.game.paddles:
                if not player.ishuman:
                    continue
                if player.orientation == "vertical":
                    for y in range(player.y, player.y + player.height):
                        pixels[y][player.x] = player.color()
                else:
                    for x in range(player.x, player.x + player.height):
                        pixels[player.y][x] = player.color()
            scores = []
            for player in self.game.paddles:
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
            await self.output_frame(bytes(self.flatten(pixels)))
            if not self.on_pi:
                time_end = time()
                time_delta = time_start - time_end
                await sleep(max(0.04 - time_delta, 0))

    async def add_player(self, player):
        if not self.game:
            self.game = Game({"width": self.winw, "height": self.winh})
        paddle = next(
            (paddle for paddle in self.game.paddles if not paddle.player), None)
        if paddle:
            paddle.player = player
            paddle.ishuman = True
            player.paddle = paddle
        else:
            return

    def color(self, code):
        r, g, b = tuple(int(code[i:i + 2], 16) for i in (0, 2, 4))

        return [r, g, b]
