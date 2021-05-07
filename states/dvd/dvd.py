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

addx = 2
addy = 1

color = bytes([100, 100, 100])
background = bytes([0, 0, 0])

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
    posx += addx
    posy += addy

    if (posx <= 0 or posx >= winw - width) and (posy <= 0 or posy >= winh - height):
        for i in range(0, 10):
            stdout.buffer.write(color * (128 * 32))
            sleep(0.15)
            stdout.buffer.write(background * (128 * 32))
            sleep(0.15)

    if posx <= 0 or posx >= winw - width:
        addx *= -1
        color = change_color(color)

    if posy <= 0 or posy >= winh - height:
        addy *= -1
        color = change_color(color)

    for y in range(0, winh):
        for x in range(0, winw):
            stdout.buffer.write(get_pixel(x, y))

    sleep(0.05)
