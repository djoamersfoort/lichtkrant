import json
import socket
import threading
from random import choice
from time import sleep

from PIL import Image, ImageDraw

from states.base import BaseState


class Game:
    def __init__(self):
        self.image = Image.new("RGB", (96, 32), "black")
        self.draw = ImageDraw.Draw(self.image)
        self.food = 0
        with open("./static/pacman_assets/map.json", encoding="utf-8") as f:
            self.map = json.load(f)
        self.direction = [1, 0]
        self.prepare()
        self.position = self.map["data"]["playerSpawn"]
        self.enemies = []

        self.lastScatter = 0

        # Create enemies
        self.enemies.append(Blinky(self, self.map["data"]["spawn"]))
        self.enemies.append(Inky(self, self.map["data"]["spawn"]))
        self.enemies.append(Pinky(self, self.map["data"]["spawn"]))
        self.enemies.append(Clyde(self, self.map["data"]["spawn"]))

        self.time = 0
        self.lost = False

    def prepare(self):
        for y, row in enumerate(self.map["map"]):
            for x, _ in enumerate(row):
                self.draw.point((x, y), (0, 0, 0))
                self.redraw(x, y)

    def redraw(self, x, y):
        tile = self.map["map"][y][x]
        # 1 = wall
        # 2 = food
        # 3 = enemy spawn
        # 4 = player spawn
        # 5 = teleport
        # 6 = boost

        if tile == 0:
            self.draw.point((x, y), (0, 0, 0))
        if tile == 1:
            self.draw.point((x, y), (16, 43, 200))
        if tile == 2:
            self.food += 1
            self.draw.point((x, y), (150, 150, 150))
        if tile == 5:
            self.draw.point((x, y), (128, 0, 128))
        if tile == 6:
            self.draw.point((x, y), (1, 255, 255))

    def update(self, direction):
        # win check
        if self.food == 0:
            self.lost = True

        if self.time - self.lastScatter == 140:
            for enemy in self.enemies:
                enemy.scattering = False

        # only move player once every 4 ticks
        if self.time % 4 == 0:
            virt_pos = {"x": self.position["x"] + direction[0], "y": self.position["y"] + direction[1]}
            if not self.map["map"][virt_pos["y"]][virt_pos["x"]] == 1:
                self.direction = direction

            self.draw.point((self.position["x"], self.position["y"]), (0, 0, 0))
            new_pos = {"x": self.position["x"] + self.direction[0], "y": self.position["y"] + self.direction[1]}
            tile = self.map["map"][new_pos["y"]][new_pos["x"]]
            if not tile == 1:
                self.redraw(self.position["x"], self.position["y"])
                self.position = new_pos
            if tile == 2:
                self.food -= 1
                self.map["map"][new_pos["y"]][new_pos["x"]] = 0
            if tile == 5:
                if self.position == self.map["data"]["teleports"][0]:
                    self.position = self.map["data"]["teleports"][1]
                else:
                    self.position = self.map["data"]["teleports"][0]
            if tile == 6:
                self.food -= 1
                self.map["map"][new_pos["y"]][new_pos["x"]] = 0
                for enemy in self.enemies:
                    enemy.scattering = True
                self.lastScatter = self.time

            self.draw.point((self.position["x"], self.position["y"]), (255, 251, 0))
            self.check_lost()

        if self.time % 5 == 0:
            for i, enemy in enumerate(self.enemies):
                self.draw.point((enemy.position["x"], enemy.position["y"]), (0, 0, 0))

                new_pos = {"x": enemy.position["x"] + enemy.direction["x"],
                           "y": enemy.position["y"] + enemy.direction["y"]}
                self.redraw(enemy.position["x"], enemy.position["y"])
                enemy.position = new_pos

                tile = self.map["map"][new_pos["y"]][new_pos["x"]]
                if tile == 5:
                    if enemy.position == self.map["data"]["teleports"][0]:
                        enemy.position = self.map["data"]["teleports"][1]
                    else:
                        enemy.position = self.map["data"]["teleports"][0]

                if self.time > i * 30:
                    if not enemy.scattering:
                        enemy.update()
                    else:
                        enemy.scatter()

                if not enemy.scattering:
                    self.draw.point((enemy.position["x"], enemy.position["y"]), enemy.color)
                else:
                    self.draw.point((enemy.position["x"], enemy.position["y"]), (35, 33, 240))
                    if self.time - self.lastScatter > 100 and int(self.time / 10) % 2 == 0:
                        self.draw.point((enemy.position["x"], enemy.position["y"]), (255, 255, 255))

            self.check_lost()

        self.time += 1

    def check_lost(self):
        lost = False
        for enemy in self.enemies:
            if enemy.position["x"] == self.position["x"] and enemy.position["y"] == self.position["y"]:
                if enemy.scattering:
                    enemy.position = self.map["data"]["spawn"]
                    enemy.direction = {"x": 0, "y": 0}
                    enemy.scattering = False
                else:
                    lost = True

        if lost:
            self.lost = True


class State(BaseState):
    name = "pacman"
    index = 8
    delay = 5
    game = None
    source = ""
    direction = [1, 0]

    def __init__(self):
        super().__init__()
        threading.Thread(target=self.receive).start()

    def check(self, _state):
        return self.game

    def run(self):
        while not self.killed:
            if self.game:
                self.game.update(self.direction)
                self.output_image(self.game.image)

                if self.game.lost:
                    self.game = Game()

            sleep(0.05)

    def receive(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            s.bind(("0.0.0.0", 3564))
            s.listen()
            while not self.killed:
                conn, addr = s.accept()
                threading.Thread(target=self.msg, args=(conn, addr)).start()

    def move(self, movement):
        if not len(movement) == 4:
            return

        if movement[0] == "1":
            self.direction = [0, -1]
        if movement[1] == "1":
            self.direction = [-1, 0]
        if movement[2] == "1":
            self.direction = [0, 1]
        if movement[3] == "1":
            self.direction = [1, 0]

    def msg(self, conn, _addr):
        playing = False

        while not self.killed:
            data = b''
            try:
                data = conn.recv(7)
                conn.send(b"_")
            except Exception:
                if playing:
                    self.game = None
            if not self.game:
                playing = True
                self.game = Game()

            request = data.decode().strip()
            if not playing:
                continue

            self.move(request)


class Enemy:
    def __init__(self, game, pos):
        self.position = pos
        self.direction = {"x": 0, "y": 0}
        self.game = game
        self.scattering = False

    def ideal_direction(self, position):
        the_map = self.game.map["map"]

        distances = [
            {"direction": "up", "distance": self.position["y"] - position["y"]},
            {"direction": "down", "distance": position["y"] - self.position["y"]},
            {"direction": "left", "distance": self.position["x"] - position["x"]},
            {"direction": "right", "distance": position["x"] - self.position["x"]}
        ]
        distances.sort(key=lambda d: d["distance"])
        for distance in distances:
            if distance["direction"] == "up":
                if not the_map[self.position["y"] + 1][self.position["x"]] == 1:
                    if self.direction["y"] != -1:
                        return {"x": 0, "y": 1}
            if distance["direction"] == "down":
                if not the_map[self.position["y"] - 1][self.position["x"]] == 1:
                    if self.direction["y"] != 1:
                        return {"x": 0, "y": -1}
            if distance["direction"] == "left":
                if not the_map[self.position["y"]][self.position["x"] + 1] == 1:
                    if self.direction["x"] != -1:
                        return {"x": 1, "y": 0}
            if distance["direction"] == "right":
                if not the_map[self.position["y"]][self.position["x"] - 1] == 1:
                    if self.direction["x"] != 1:
                        return {"x": -1, "y": 0}

        return {"x": 0, "y": 0}

    def update(self):
        self.direction = self.ideal_direction(self.game.position)


class Blinky(Enemy):
    color = (247, 1, 0)

    def scatter(self):
        self.direction = self.ideal_direction({"x": 95, "y": 1})


class Inky(Enemy):
    color = (0, 197, 197)

    def update(self):
        pacman_direction = self.ideal_direction(self.game.position)
        blinky_direction = self.ideal_direction(self.game.enemies[0].position)
        directions = [pacman_direction, pacman_direction, blinky_direction]

        self.direction = choice(directions)

    def scatter(self):
        self.direction = self.ideal_direction({"x": 95, "y": 31})


class Pinky(Enemy):
    color = (247, 178, 247)

    def update(self):
        pacman_soon = {**self.game.position}
        pacman_soon["x"] += self.game.direction[0]
        pacman_soon["y"] += self.game.direction[1]

        self.direction = self.ideal_direction(pacman_soon)

    def scatter(self):
        self.direction = self.ideal_direction({"x": 1, "y": 1})


class Clyde(Enemy):
    color = (235, 173, 70)

    def update(self):
        pacman = self.game.position
        position = self.position

        if pacman["x"] - position["x"] > 4 or pacman["x"] - position["x"] < -4:
            if pacman["y"] - position["y"] > 4 or pacman["y"] - position["y"] < -4:
                self.direction = self.ideal_direction(pacman)
                return

        self.scatter()

    def scatter(self):
        self.direction = self.ideal_direction({"x": 1, "y": 31})
