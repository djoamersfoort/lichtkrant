import threading
from random import randrange
from time import sleep

from PIL import Image, ImageDraw

from states.base import BaseState

DIMENSIONS = (96, 32)


class Player:
    def __init__(self, socket, state):
        self.socket = socket
        self.active = True
        self.color = "FFFFFF"
        self.direction = (0, 1)
        self.position = (0, 0)
        self.elements = [(DIMENSIONS[0] / 2, DIMENSIONS[1] / 2), (DIMENSIONS[0] / 2, DIMENSIONS[1] - 1)]
        self.size = 2
        self.dead = False
        self.state = state
        socket.on_color(self.set_color)
        socket.on_press(self.turn)
        socket.on_leave(self.leave)

    def set_color(self, color):
        self.color = color.lstrip("#")

    def leave(self):
        self.active = False

    def reset(self):
        self.direction = (0, 1)
        self.elements = [(DIMENSIONS[0] / 2, DIMENSIONS[1] / 2), (DIMENSIONS[0] / 2, DIMENSIONS[1] / 2 - 1)]
        self.size = 2
        self.dead = False

    def checkDeath(self):
        if self.elements[0][0] <= 0 or self.elements[0][1] <= 0:
            return True
        if self.elements[0][0] >= DIMENSIONS[0] - 1 or self.elements[0][1] >= DIMENSIONS[1] - 1:
            return True

        return False

    def turn(self, direction):
        if direction == "w":
            self.direction = (0, -1)
        elif direction == "a":
            self.direction = (-1, 0)
        elif direction == "s":
            self.direction = (0, 1)
        elif direction == "d":
            self.direction = (1, 0)

    def newPos(self):
        return self.elements[0][0] + self.direction[0], self.elements[0][1] + self.direction[1]

    def update(self):
        if self.size <= len(self.elements):
            self.elements.pop()
        if self.size >= len(self.elements):
            self.elements.insert(0, self.newPos())

        self.dead = self.checkDeath()


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
    def __init__(self):
        self.location = (0, 0)
        self.newLoc()

    def newLoc(self):
        self.location = (randrange(1, DIMENSIONS[0] - 2), randrange(1, DIMENSIONS[1] - 2))


class Game:
    def __init__(self, state):
        self.players = []
        self.apples = []
        self.bodies = []
        self.state = state

    def add_player(self, player):
        self.players.append(Player(player, self.state))
        self.apples.append(Apple())

    @staticmethod
    def hex_to_rgb(code):
        return tuple(int(code[i:i + 2], 16) for i in (0, 2, 4))

    def update(self, tick):
        for player in self.players:
            if not player.active:
                continue
            speed = 30 - round(len(player.elements) / 2)
            speed = max(speed, 5)

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
                    apple.newLoc()

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
        draw.rectangle([(0, 0), (DIMENSIONS[0] - 1, DIMENSIONS[1] - 1)], outline=(250, 128, 114))

        return image


class State(BaseState):
    def __init__(self):
        super().__init__()
        self.name = "snake"
        self.index = 8
        self.delay = 5
        self.is_game = True
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
