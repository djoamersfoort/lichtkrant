from time import sleep
from sys import stdout
from random import randint

width = 24
height = 4

winw = 128
winh = 32

posx = randint(0, winw - width - 1)
posy = randint(0, winh - height - 1)

addx = 2
addy = 1

color = bytes([100, 100, 100])
background = bytes([0, 0, 0])

while True:
    posx += addx
    posy += addy

    if (posx <= 0 or posx >= winw - width) and (posy <= 0 or posy >= winh - height):
        for i in range(0, 10):
            stdout.buffer.write(color * (128 * 32))
            sleep(0.15)
            stdout.buffer.write(background * (128 * 32))
            sleep(0.15)

    if posx <= 0 or posx >= winw - width: addx *= -1
    if posy <= 0 or posy >= winh - height: addy *= -1

    for y in range(0, winh):
        for x in range(0, winw):
            stdout.buffer.write(color if (x >= posx and x <= posx + width) and (y >= posy and y <= posy + height) else background)

    sleep(0.03)
