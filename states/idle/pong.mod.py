from sys import stdout
from time import sleep
import random

# module information
name = "pong"
index = 0
delay = 30


# check function
def check(state):
    return True


winw = 96
winh = 32
offset = 6
height = 8

color = bytes([255, 255, 255])
frame_delay = 1/30


# module runner
def run():
    p1_y = 16
    p2_y = 16

    posx = winw / 2
    posy = winh / 2
    addx = 1
    addy = 1

    # variables
    def get_pixel(x, y):
        if x == posx and y == posy:
            return color

        if x == offset and (y < p1_y + height and y > p1_y - height):
            return color

        if x == winw - offset and (y < p2_y + height and y > p2_y - height):
            return color

        if x == winw / 2 and y % 2 == 0:
            return color

        return bytes([0, 0, 0])

    def move_paddle(px, py):
        up = posy > py

        if abs(px - posx) > winw / 2:
            up = not up

        if random.randint(0, 10) < 8:
            if up and py + offset < winh - 3:
                py += 1
            elif not up and py - offset > 2:
                py -= 1

        return py

    def check_hit(px, py):
        return posx == px and py > posy - height and py < posy + height

    # 'game' loop
    while True:
        posx += addx
        posy += addy

        hit_paddle = check_hit(offset, p1_y) or check_hit(winw - offset, p2_y)
        hit_edge_h = posx <= 0 or posx >= winw - 1
        hit_edge_v = posy <= 0 or posy >= winh - 1

        if hit_edge_v:
            addy *= -1

        if hit_edge_h:
            posx = winw / 2
            posy = winh / 2

        if hit_paddle:
            addx *= -1

        p1_y = move_paddle(offset, p1_y)
        p2_y = move_paddle(winw - offset, p2_y)

        for y in range(0, winh):
            for x in range(0, winw):
                stdout.buffer.write(get_pixel(x, y))

        sleep(frame_delay)
