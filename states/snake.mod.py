import threading
import socket
from time import sleep, time
from random import randrange

from states.base import BaseState

BLUE = [0, 0, 255]
RED = [255, 0, 0]

class Game: 
    def __init__(self, dims):
        self.dims = dims
        h = self.dims["height"]
        w = self.dims["width"]
        self.reset()
        

    def reset(self):
        self.snake = [[int(self.dims["width"] / 2), int(self.dims["height"] / 2)], [int(self.dims["width"] / 2), int(self.dims["height"] / 2 - 1)]]
        self.apples = []
        self.addApple()
        self.addApple()
        self.addApple()
        self.direction = [0, -1]
        self.slowness = 3
        self.count = 0
        self.dead = False

    def addApple(self):
        self.apples.append([randrange(self.dims["width"]), randrange(self.dims["height"])])

    def checkDeath(self):
        for index, pixel in enumerate(self.snake): 
            if self.snake[0] == pixel and not index == 0:
                return True

        if self.snake[0][0] < 0 or self.snake[0][0] >= self.dims["width"] or self.snake[0][1] < 0 or self.snake[0][1] >= self.dims["height"]:
            return True

        return False

    def checkApple(self):
        for index, apple in enumerate(self.apples):
            if self.snake[0] == apple: 
                self.addApple()
                self.apples.remove(apple)

                if self.slowness > 0:
                    self.slowness -= 0.11
                return True

        return False

    def turn(self, direction):
        if direction == "w" and not self.direction == [0, 1]:
            self.direction = [0, -1]
        if direction == "a" and not self.direction == [1, 0]:
            self.direction = [-1, 0]
        if direction == "s" and not self.direction == [0, -1]:
            self.direction = [0, 1]
        if direction == "d" and not self.direction == [-1, 0]:
            self.direction = [1, 0]

    def update(self):
        if self.count == int(self.slowness):
            if not self.checkApple():
                self.snake.pop()
            self.snake.insert(0, [self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1]])

            self.dead = self.checkDeath()
            self.count = -1
        self.count += 1
        

class State(BaseState):
    name = "Snake"
    index = 7
    delay = 5
    game = None
    connections = 0

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
                if not self.on_pi:
                    time_start = time()
                
                self.game.update()

                pixels = []
                for _ in range(self.winh):
                    pixels.append([])
                    for _ in range(self.winw):
                        pixels[-1].append([0, 0, 0])

                if self.game.dead:
                    for y, row in enumerate(self.text("game over!")):
                        for x, pixel in enumerate(row):
                            if pixel:
                                pixels[y + 1][x] = RED


                else:
                    for pixel in self.game.apples:
                        pixels[pixel[1]][pixel[0]] = RED
                    for pixel in self.game.snake:
                        pixels[pixel[1]][pixel[0]] = BLUE

                self.output_frame(bytes(self.flatten(pixels)))
                if self.game.dead:
                    sleep(2)
                    self.game.reset()

                if not self.on_pi:
                    time_end = time()
                    time_delta = time_start - time_end
                    sleep(max(0.04-time_delta, 0))

    def receive(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            s.bind(("0.0.0.0", 1029))
            s.listen()
            while not self.killed:
                conn, addr = s.accept()
                threading.Thread(target=self.msg, args=(conn, addr)).start()

    def msg(self, conn, _addr):
        self.connections += 1
        while not self.killed:
            data = b''
            try:
                data = conn.recv(1)
                conn.send(b"_")

            except Exception:
                self.connections -= 1
                if self.connections == 0:
                    self.game = None

                break
            
            if not self.game:
                self.game = Game({"width": self.winw, "height": self.winh})

            request = data.decode().strip()
            self.game.turn(request)