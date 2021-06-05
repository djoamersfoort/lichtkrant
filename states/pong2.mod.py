from time import sleep
import random
import threading
import socket
from states.base import BaseState


class State(BaseState):

    # module information
    name = "pong2"
    index = 7
    delay = 30

    winw = 96
    winh = 32
    offset = 6
    height = 8

    color = bytes([255, 255, 255])
    blue = bytes([0, 0, 255])
    red = bytes([255, 0, 0])
    green = bytes([0, 255, 0])
    frame_delay = 1 / 30

    def __init__(self):
        super().__init__()
        self.context = {
            "p1_isplaying": False,
            "p2_isplaying": False,
            "p1_movement": 0,
            "p2_movement": 0,
            "killed": False
        }
        threading.Thread(target=self.receive, args=(self.context,)).start()

    def kill(self):
        self.context["killed"] = True
        super().kill()

    # check function
    def check(self, state):
        if self.context["p1_isplaying"] or self.context["p2_isplaying"]:
            return True

    # module runner
    def run(self):
        p1_y = 16
        p2_y = 16
        p1_points = 0
        p2_points = 0

        posx = self.winw / 2
        posy = self.winh / 2
        addx = 1
        addy = 1

        def number(xstart, ystart, number, color):
            if x == xstart and y == ystart:
                if number == 0 or number == 2 or number == 3 or number == 4 or number == 5 or number == 6:
                    return color
            if x == xstart + 1 and y == ystart:
                if number == 0 or number == 2 or number == 3 or number == 5 or number == 6:
                    return color
            if x == xstart + 2 and y == ystart:
                if number == 0 or number == 1 or number == 2 or number == 3 or number == 4 or number == 5 or number == 6:
                    return color
            if x == xstart and y == ystart + 1:
                if number == 0 or number == 4 or number == 5 or number == 6:
                    return color
            if x == xstart + 2 and y == ystart + 1:
                if number == 0 or number == 1 or number == 2 or number == 3 or number == 4:
                    return color
            if x == xstart and y == ystart + 2:
                if number == 0 or number == 2 or number == 3 or number == 4 or number == 5 or number == 6:
                    return color
            if x == xstart + 1 and y == ystart + 2:
                if number == 2 or number == 3 or number == 4 or number == 5 or number == 6:
                    return color
            if x == xstart + 2 and y == ystart + 2:
                if number == 0 or number == 1 or number == 2 or number == 3 or number == 4 or number == 5 or number == 6:
                    return color
            if x == xstart and y == ystart + 3:
                if number == 0 or number == 2 or number == 6:
                    return color
            if x == xstart + 2 and y == ystart + 3:
                if number == 0 or number == 1 or number == 3 or number == 4 or number == 5 or number == 6:
                    return color
            if x == xstart and y == ystart + 4:
                if number == 0 or number == 2 or number == 3 or number == 5 or number == 6:
                    return color
            if x == xstart + 1 and y == ystart + 4:
                if number == 0 or number == 2 or number == 3 or number == 5 or number == 6:
                    return color
            if x == xstart + 2 and y == ystart + 4:
                if number == 0 or number == 1 or number == 2 or number == 3 or number == 4 or number == 5 or number == 6:
                    return color
            return bytes([0, 0, 0])

        # variables
        def get_pixel(x, y, p1_win, p2_win):
            if x == posx and y == posy:
                return self.color

            if x == self.offset and (p1_y + self.height > y > p1_y - self.height):
                if p1_win:
                    return self.green
                else:
                    if self.context["p1_isplaying"]:
                        return self.blue
                    else:
                        return self.color

            if x == self.winw - self.offset and (p2_y + self.height > y > p2_y - self.height):
                if p2_win:
                    return self.green
                else:
                    if self.context["p2_isplaying"]:
                        return self.blue
                    else:
                        return self.color

            if x == self.winw / 2 and y % 2 == 0:
                return self.color

            if x == self.winw / 2 and y % 2 == 0:
                return self.color

            if x == 0:
                return self.red

            if x == 95:
                return self.red

            if 49 < x < 53 and 25 < y < 31:
                if p2_win:
                    return number(50, 26, p2_points, self.green)
                else:
                    return number(50, 26, p2_points, self.color)

            if 47 > x > 43 and 25 < y < 31:
                if p1_win:
                    return number(44, 26, p1_points, self.green)
                else:
                    return number(44, 26, p1_points, self.color)

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

            p1_win = False
            p2_win = False
            posx += addx
            posy += addy

            hit_paddle = check_hit(self.offset, p1_y) or check_hit(self.winw - self.offset, p2_y)
            hit_edge_h = posx <= 0 or posx >= self.winw - 1
            hit_edge_v = posy <= 0 or posy >= self.winh - 1

            if hit_edge_v:
                addy *= -1

            if hit_edge_h:
                if posx <= 0:
                    p2_points += 1
                    if p2_points == 7:
                        p2_points = 0
                        p1_points = 0
                        p2_win = True
                else:
                    p1_points += 1
                    if p1_points == 7:
                        p2_points = 0
                        p1_points = 0
                        p1_win = True
                posx = self.winw / 2
                posy = self.winh / 2

            if hit_paddle:
                addy *= -1
                addx *= -1

            if self.context["p1_isplaying"]:
                if self.context["p1_movement"] == 1:
                    p1_y += 1
                elif self.context["p1_movement"] == -1:
                    p1_y -= 1
                if p1_y < 8:
                    p1_y = 8
                if p1_y > 23:
                    p1_y = 23
            else:
                p1_y = move_paddle(self.offset, p1_y)

            if self.context["p2_isplaying"]:
                if self.context["p2_movement"] == 1:
                    p2_y += 1
                elif self.context["p2_movement"] == -1:
                    p2_y -= 1
                if p2_y < 8:
                    p2_y = 8
                if p2_y > 23:
                    p2_y = 23
            else:
                p2_y = move_paddle(self.winw - self.offset, p2_y)

            frame = b''
            for y in range(0, self.winh):
                for x in range(0, self.winw):
                    frame += get_pixel(x, y, p1_win, p2_win)
            self.output_frame(frame)

            if p1_win or p2_win:
                frame = b''
                for y in range(0, self.winh):
                    for x in range(0, self.winw):
                        frame += get_pixel(x, y, p1_win, p2_win)

                for i in range(150):
                    self.output_frame(frame)
                    sleep(self.frame_delay)

            sleep(self.frame_delay)

    def receive(self, context):
        HOST = '0.0.0.0'  # Standard loopback interface address (localhost)
        PORT = 9999  # Port to listen on (non-privileged ports are > 1023)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            s.bind((HOST, PORT))
            s.listen()
            while not context['killed']:
                conn, addr = s.accept()
                threading.Thread(target=self.handleclient, args=(conn, addr, context)).start()

    def handleclient(self, conn, addr, context):
        player = None
        while not context['killed']:
            try:
                data = conn.recv(1)
            except:
                if player == '1':
                    context["p1_isplaying"] = False
                else:
                    context["p2_isplaying"] = False
                break
            if data.decode() != "":
                if player is None:
                    if data.decode() == '1' or data.decode() == '2':
                        if data.decode() == '1':
                            if context["p1_isplaying"]:
                                msg = "redSomeone is already player 1"
                            else:
                                context["p1_isplaying"] = True
                                msg = "yellowYou are player 1"
                                player = "1"
                        if data.decode() == '2':
                            if context["p2_isplaying"]:
                                msg = "redSomeone is already player 2"
                            else:
                                context["p2_isplaying"] = True
                                msg = "yellowYou are player 2"
                                player = "2"
                    else:
                        msg = "redUnknown"

                else:
                    if data.decode() == 'w':
                        msg = "greenup"
                        if player == '1':
                            context["p1_movement"] = -1
                        else:
                            context["p2_movement"] = -1

                    elif data.decode() == 's':
                        if player == '1':
                            context["p1_movement"] = 1
                        else:
                            context["p2_movement"] = 1
                        msg = 'greendown'
                    else:
                        msg = 'redUnknown'
            else:
                msg = 'redUnknown'

            try:
                conn.send(msg.encode())
            except:
                if player == '1':
                    context["p1_isplaying"] = False
                else:
                    context["p2_isplaying"] = False
                break
