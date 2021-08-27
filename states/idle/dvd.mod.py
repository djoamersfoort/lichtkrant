from time import sleep
from random import randint
from states.base import BaseState


class State(BaseState):

    # module information
    name = "dvd"
    index = 0
    delay = 45

    # check function
    def check(self, state):
        return True

    # DJO logo
    logo = [
        [0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0],
        [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
        [0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0]
    ]

    height = len(logo) - 1
    width = len(logo[0]) - 1

    winw = 96
    winh = 32

    frame_delay = 1/30

    # module runner
    def run(self):
        # variables
        posx = randint(0, self.winw - self.width - 2)
        posy = randint(0, self.winh - self.height - 2)

        addx = 1
        addy = 1

        color = bytes([100, 100, 100])
        background = bytes([0, 0, 0])
        flash_brightness = 0

        # change to a random color
        def change_color(color):
            new_color = [color[0], color[1], color[2]]
            to_change = randint(0, 2)

            new_color[to_change] += randint(-128, 128)

            if new_color[to_change] > 255:
                new_color[to_change] -= 255
            if new_color[to_change] < 0:
                new_color[to_change] += 255

            return bytes(new_color)

        # get a pixel on the screen
        def get_pixel(x, y):
            if x < posx or x > posx + self.width or y < posy or y > posy + self.height:
                return background

            return color if self.logo[y - posy][x - posx] == 1 else background

        # 'game' loop
        while not self.killed:
            posx += addx
            posy += addy

            horizontal_hit = posx <= 0 or posx >= self.winw - self.width - 1
            vertical_hit = posy <= 0 or posy >= self.winh - self.height - 1

            if horizontal_hit and vertical_hit:
                for _i in range(0, 5):
                    while flash_brightness < 240:
                        self.output_frame(bytes([flash_brightness, flash_brightness, flash_brightness]) * 3072)
                        flash_brightness += 20
                        sleep(0.05)
                    while flash_brightness > 0:
                        self.output_frame(bytes([flash_brightness, flash_brightness, flash_brightness]) * 3072)
                        flash_brightness -= 20
                        sleep(0.05)

            if horizontal_hit:
                addx *= -1
                color = change_color(color)
            if vertical_hit:
                addy *= -1
                color = change_color(color)

            frame = b''
            for y in range(0, self.winh):
                for x in range(0, self.winw):
                    frame += get_pixel(x, y)

            for _i in range(2):
                self.output_frame(frame)
                sleep(self.frame_delay)