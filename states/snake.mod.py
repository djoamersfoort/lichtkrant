import threading
import socket
from time import sleep, time
from PIL import Image, ImageDraw, ImageFont, ImageColor
from random import randrange

from states.base import BaseState

DIMENSIONS = (96, 32)


class Player:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.active = True
        self.color = "FFFFFF"
        self.direction = (0, 1)
        self.position = (0, 0)
        self.elements = [(DIMENSIONS[0] / 2, DIMENSIONS[1] / 2), (DIMENSIONS[0] / 2, DIMENSIONS[1] - 1)]
        self.size = 2
        self.dead = False
        threading.Thread(target=self.msg).start()

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
        if not len(direction) == 4:
            return

        if direction[0] == "1" and not self.direction == (0, 1):
            self.direction = (0, -1)
        if direction[1] == "1" and not self.direction == (1, 0):
            self.direction = (-1, 0)
        if direction[2] == "1" and not self.direction == (0, -1):
            self.direction = (0, 1)
        if direction[3] == "1" and not self.direction == (-1, 0):
            self.direction = (1, 0)

    def msg(self):
        while self.active:
            data = b''
            try:
                data = self.conn.recv(7)
                self.conn.send(b'')
            except Exception:
                self.active = False

            request = data.decode().strip()
            if len(request) == 7 and request.startswith("#"):
                self.color = request.lstrip("#")
            self.turn(request)

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
        if new < 0:
            new = 0
        return new

    def fade(self):
        self.color = (self.sub(self.color[0]), self.sub(self.color[1]), self.sub(self.color[2]))


class Apple:
    def __init__(self):
        self.location = (0, 0)
        self.newLoc()

    def newLoc(self):
        self.location = (randrange(1, DIMENSIONS[0] - 2), randrange(1, DIMENSIONS[1] - 2))


class Game:
    def __init__(self):
        self.players = []
        self.apples = []
        self.bodies = []
        threading.Thread(target=self.receive).start()

    @staticmethod
    def hex_to_rgb(code):
        return tuple(int(code[i:i + 2], 16) for i in (0, 2, 4))

    def update(self, tick):
        for player in self.players:
            if not player.active:
                continue
            speed = 30 - round(len(player.elements) / 2)
            if speed < 5:
                speed = 5

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

    def receive(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            s.bind(("0.0.0.0", 1029))
            s.listen()
            while True:
                conn, addr = s.accept()
                player = Player(conn, addr)
                self.players.append(player)
                self.apples.append(Apple())


class State(BaseState):
    def __init__(self):
        super().__init__()
        self.name = "snake"
        self.index = 8
        self.delay = 5
        self.game = Game()

    def check(self, _state):
        return len(self.game.players) > 0

    def run(self):
        tick = 0
        while not self.killed:
            tick += 1
            self.game.update(tick)
            self.output_image(self.game.export())

            sleep(0.01)
