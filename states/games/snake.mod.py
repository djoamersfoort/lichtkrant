from random import randrange
from time import sleep

from PIL import Image, ImageDraw

from states.base import BaseState
from states.socket import BasePlayer

DIMENSIONS = (96, 32)


class Player(BasePlayer):
    def __init__(self, sio, sid, game):
        super().__init__(sio, sid, game)
        self.active = True
        self.color = "FFFFFF"
        self.direction = (0, 1)
        self.new_direction = (0, 1)
        self.position = (0, 0)
        self.elements = [(DIMENSIONS[0] / 2, DIMENSIONS[1] / 2), (DIMENSIONS[0] / 2, DIMENSIONS[1] - 1)]
        self.size = 2
        self.dead = False

    def on_color(self, code):
        self.color = code.lstrip("#")

    def on_leave(self):
        self.active = False
        self.game.apples.pop()

    def reset(self):
        self.direction = (0, 1)
        self.elements = [(DIMENSIONS[0] / 2, DIMENSIONS[1] / 2), (DIMENSIONS[0] / 2, DIMENSIONS[1] / 2 - 1)]
        self.size = 2
        self.dead = False

    def check_death(self):
        if self.elements[0][0] <= 0 or self.elements[0][1] <= 0:
            return True
        if self.elements[0][0] >= DIMENSIONS[0] - 1 or self.elements[0][1] >= DIMENSIONS[1] - 1:
            return True

        return False

    def on_press(self, key):
        if key == "w" and not self.direction[1] == 1:
            self.new_direction = (0, -1)
        elif key == "a" and not self.direction[0] == 1:
            self.new_direction = (-1, 0)
        elif key == "s" and not self.direction[1] == -1:
            self.new_direction = (0, 1)
        elif key == "d" and not self.direction[0] == -1:
            self.new_direction = (1, 0)

    def new_pos(self):
        return self.elements[0][0] + self.direction[0], self.elements[0][1] + self.direction[1]

    def update(self):
        self.direction = self.new_direction

        if self.size <= len(self.elements):
            self.elements.pop()
        if self.size >= len(self.elements):
            self.elements.insert(0, self.new_pos())

        self.dead = self.check_death()


class Body:
    def __init__(self, color, elements):
        self.color = color
        self.elements = elements
        self.opacity = 1

    @staticmethod
    def sub(current):
        new = current - 1
        return max(new, 0)

    def fade(self):
        self.color = (self.sub(self.color[0]), self.sub(self.color[1]), self.sub(self.color[2]))


class Apple:
    def __init__(self, game):
        self.location = (0, 0)
        self.game = game
        self.new_loc()

    def new_loc(self):
        new_location = (randrange(1, DIMENSIONS[0] - 2), randrange(1, DIMENSIONS[1] - 2))
        for player in self.game.players:
            for element in player.elements:
                if new_location == element:
                    return self.new_loc()

        self.location = new_location


class Game:
    def __init__(self, state):
        self.players = []
        self.apples = []
        self.bodies = []
        self.state = state

    def add_player(self, player):
        self.players.append(player)
        self.apples.append(Apple(self))

    @staticmethod
    def hex_to_rgb(code):
        return tuple(int(code[i:i + 2], 16) for i in (0, 2, 4))

    def update(self, tick):
        for player in self.players:
            if not player.active:
                self.players.remove(player)
                continue
            speed = 30 - round(len(player.elements) / 3)
            speed = max(speed, 7)

            if tick % speed == 0:
                player.update()
                for p2 in self.players:
                    for index, element in enumerate(p2.elements):
                        if p2 == player and index == 0:
                            continue
                        if element == player.elements[0]:
                            player.dead = True

                if player.dead:
                    self.bodies.append(Body(self.hex_to_rgb(player.color), player.elements))
                    player.reset()

            for apple in self.apples:
                if player.elements[0] == apple.location:
                    player.size += 1
                    apple.new_loc()

        for body in self.bodies:
            body.fade()

    def export(self):
        image = Image.new("RGB", DIMENSIONS, "black")
        draw = ImageDraw.Draw(image)
        for body in self.bodies:
            for element in body.elements:
                draw.point(element, fill=body.color)
        for player in self.players:
            if not player.active:
                continue
            for element in player.elements:
                draw.point(element, fill=self.hex_to_rgb(player.color))
        for apple in self.apples:
            draw.point(apple.location, fill=(255, 0, 0))
        draw.rectangle((0, 0, DIMENSIONS[0] - 1, DIMENSIONS[1] - 1), outline=(250, 128, 114))

        return image


class State(BaseState):
    def __init__(self):
        super().__init__()
        self.name = "snake"
        self.game_meta = "static/game_meta/snake.json"
        self.index = 8
        self.delay = 5
        self.player_class = Player
        self.game = Game(self)

    def add_player(self, player):
        self.game.add_player(player)

    def check(self, _state):
        return len(self.game.players) > 0

    def run(self):
        tick = 0
        while not self.killed:
            tick += 1
            self.game.update(tick)
            self.output_image(self.game.export())

            sleep(0.01)
