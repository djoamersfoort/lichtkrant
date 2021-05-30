from sys import stdout
from time import sleep
from states.base import BaseState
import random


class State(BaseState):
    # module information
    name = "pong"
    index = 0
    delay = 30

    winw = 96
    winh = 32
    offset = 6
    height = 8

    color = bytes([255, 255, 255])
    frame_delay = 1 / 30

    # check function
    def check(self, state):
        self.state = state
        return True

    # module runner
    def run(self):
        p1_y = 16
        p2_y = 16

        posx = self.winw / 2
        posy = self.winh / 2
        addx = 1
        addy = 1

        # variables
        def get_pixel(x, y):
            if x == posx and y == posy:
                return self.color

            if x == self.offset and (p1_y + self.height > y > p1_y - self.height):
                return self.color

            if x == self.winw - self.offset and (p2_y + self.height > y > p2_y - self.height):
                return self.color

            if x == self.winw / 2 and y % 2 == 0:
                return self.color

            return bytes([0, 0, 0])

        def move_paddle(px, py):
            up = posy > py

            if abs(px - posx) > self.winw / 2:
                up = not up

            if random.randint(0, 10) < 8:
                if up and py + self.offset < self.winh - 3:
                    py += 1
                elif not up and py - self.offset > 2:
                    py -= 1

            return py

        def check_hit(px, py):
            return posx == px and posy - self.height < py < posy + self.height

        # 'game' loop
        while not self.killed:
            posx += addx
            posy += addy

            hit_paddle = check_hit(self.offset, p1_y) or check_hit(self.winw - self.offset, p2_y)
            hit_edge_h = posx <= 0 or posx >= self.winw - 1
            hit_edge_v = posy <= 0 or posy >= self.winh - 1

            if hit_edge_v:
                addy *= -1

            if hit_edge_h:
                posx = self.winw / 2
                posy = self.winh / 2

            if hit_paddle:
                addx *= -1

            p1_y = move_paddle(self.offset, p1_y)
            p2_y = move_paddle(self.winw - self.offset, p2_y)

            frame = b''
            for y in range(0, self.winh):
                for x in range(0, self.winw):
                    frame += get_pixel(x, y)
            stdout.buffer.write(frame)
            sleep(self.frame_delay)
