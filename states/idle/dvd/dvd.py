from time import sleep
from sys import stdout
from random import randint
from logo import logo

height = len(logo) - 1
width = len(logo[0]) - 1

winw = 96
winh = 32

posx = randint(0, winw - width - 1)
posy = randint(0, winh - height - 1)

addx = 1
addy = 1

color = bytes([100, 100, 100])
background = bytes([0, 0, 0])

frame = 0
frame_wrap = 1

frame_delay = 1/30


def change_color(color):
    new_color = [color[0], color[1], color[2]]
    to_change = randint(0, 2)

    new_color[to_change] += randint(-128, 128)

    if new_color[to_change] > 255:
        new_color[to_change] -= 255
    if new_color[to_change] < 0:
        new_color[to_change] += 255

    return bytes(new_color)


def get_pixel(x, y):
    if x < posx or x > posx + width or y < posy or y > posy + height:
        return background

    return color if logo[y - posy][x - posx] == 1 else background


while True:
    if frame == 0:
        posx += addx
        posy += addy

        is_left_or_right = posx <= 0 or posx >= winw - width - 1
        is_top_or_bottom = posy <= 0 or posy >= winh - height - 1

        if is_left_or_right and is_top_or_bottom:
            for i in range(0, 10):
                stdout.buffer.write(color * (128 * 32))
                sleep(0.15)
                stdout.buffer.write(background * (128 * 32))
                sleep(0.15)
        if is_left_or_right:
            addx *= -1
            color = change_color(color)
        if is_top_or_bottom:
            addy *= -1
            color = change_color(color)

    for y in range(0, winh):
        for x in range(0, winw):
            stdout.buffer.write(get_pixel(x, y))

    if frame == frame_wrap:
        frame = 0
    else:
        frame += 1

    sleep(frame_delay)
