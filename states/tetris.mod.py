import threading
import socket
from random import choice
from time import sleep, time

from states.base import BaseState


WHITE = [255, 255, 255]
GREY = [100, 100, 100]
BLACK = [0, 0, 0]
BLUE = [0, 0, 255]
GREEN = [0, 255, 0]
RED = [255, 0, 0]
CYAN = [0, 255, 255]
ORANGE = [255, 170, 0]
YELLOW = [255, 255, 0]
PURPLE = [255, 0, 255]
SHAPES = {
    "o": [[YELLOW, YELLOW], [YELLOW, YELLOW]],
    "i": [[CYAN], [CYAN], [CYAN], [CYAN]],
    "t": [[None, PURPLE, None], [PURPLE, PURPLE, PURPLE]],
    "s": [[None, GREEN, GREEN], [GREEN, GREEN, None]],
    "z": [[RED, RED, None], [None, RED, RED]],
    "j": [[BLUE, None, None], [BLUE, BLUE, BLUE]],
    "l": [[None, None, ORANGE], [ORANGE, ORANGE, ORANGE]]
}


def overlap_text(pixels, text, base_x, base_y, color=WHITE):
    for y, row in enumerate(BaseState.text(text)):
        for x, pixel in enumerate(row):
            if pixel:
                pixels[y + base_y][x + base_x] = color


def overlap_buffer(pixels, buffer, base_x, base_y):
    for y, row in enumerate(buffer):
        for x, pixel in enumerate(row):
            if pixel:
                pixels[y + base_y][x + base_x] = pixel


class Game:
    def __init__(self):
        self.boards = [Board(i) for i in range(8)]
        self.state = "lobby"  # later moves to game
        self.speed = 2
        self.steps_at_current_speed = 0
        threading.Thread(target=self.drop_pieces).start()

    def drop_pieces(self):
        while True:
            sleep(1/self.speed)
            if self.state == "game":
                for board in self.boards:
                    if board.is_alive:
                        board.move_piece_down()
                self.steps_at_current_speed += 1
                if self.steps_at_current_speed == self.speed * 50:
                    self.steps_at_current_speed = 0
                    self.speed += 1

    def update(self):
        if self.state == "game":
            for board in self.boards:
                if board.is_alive and board.in_game:
                    board.update()
            alive_boards = [
                board for board in self.boards if board.is_alive and board.in_game and board.player
            ]
            if not alive_boards:
                self.state = "winner"
                sleep(5)
                for i in range(8):
                    player = self.boards[i].player
                    self.boards[i] = Board(i)
                    self.boards[i].player = player
                    self.state = "lobby"
                    self.speed = 2
                    self.steps_at_current_speed = 0
        else:
            connected_boards = [board for board in self.boards if board.player]
            ready_boards = [
                board for board in connected_boards if board.ready_for_game
            ]
            if connected_boards and connected_boards == ready_boards:
                self.state = "game"
                for board in ready_boards:
                    board.in_game = True

    def draw(self, pixels):
        # Draw title and level counter
        if self.state == "lobby":
            overlap_text(pixels, "8 player tetris battle", 1, 3)
        else:
            overlap_text(pixels, "l", 90, 2)
            overlap_text(pixels, "v", 90, 8)
            overlap_text(pixels, "l", 90, 14)
            try:
                overlap_text(pixels, str(self.speed - 1)[-2], 90, 20)
            except IndexError:
                pass
            overlap_text(pixels, str(self.speed - 1)[-1], 90, 26)
        # Draw current places
        players = [board for board in self.boards if board.score]
        players = sorted(players, key=lambda b: b.score, reverse=True)
        for pos, board in enumerate(players):
            if pos == 0:
                overlap_text(pixels, "1", board.x + 6, 7, [210, 160, 30])
            elif pos == 1:
                overlap_text(pixels, "2", board.x + 6, 7, [190, 190, 190])
            elif pos == 2:
                overlap_text(pixels, "3", board.x + 6, 7, [205, 125, 50])
            else:
                overlap_text(pixels, str(pos + 1), board.x + 6, 7)
        # Call draw method of each board
        for board in self.boards:
            board.draw(pixels)


class Board:
    def __init__(self, index):
        self.index = index
        self.x = index * 11
        self.ready_for_game = False
        self.player = None
        self.in_game = False
        self.is_alive = True
        self.movement = {"w": 0, "a": 0, "s": 0, "d": 0, "e": 0, " ": 0}
        self.score = 0
        self.rows = [Row() for _ in range(20)]
        self.current_bag = list(SHAPES.keys())
        self.current_piece = None
        self.next_piece = None
        self.generate_new_piece()

    def generate_new_piece(self):
        self.current_piece = self.next_piece
        next_shape = choice(self.current_bag)
        self.current_bag.remove(next_shape)
        if not self.current_bag:
            self.current_bag = list(SHAPES.keys())
        self.next_piece = Piece(next_shape)
        if not self.current_piece:
            self.generate_new_piece()

    def process_movement(self, new_movement):
        if len(new_movement) != 6:
            return
        for index, key in enumerate(list("wasde ")):
            move = int(list(new_movement)[index] == "1")
            if move:
                self.movement[key] += 1
            else:
                self.movement[key] = 0
        if self.in_game:
            if self.is_alive:
                if self.movement["w"] == 1:
                    new_piece = self.current_piece.rotate()
                    if self.piece_location_valid(new_piece):
                        self.current_piece = new_piece
                if self.movement["a"] == 1:
                    new_piece = self.current_piece.move("left")
                    if self.piece_location_valid(new_piece):
                        self.current_piece = new_piece
                if self.movement["d"] == 1:
                    new_piece = self.current_piece.move("right")
                    if self.piece_location_valid(new_piece):
                        self.current_piece = new_piece
                if self.movement["e"] == 1:
                    new_piece = self.current_piece.rotate(True)
                    if self.piece_location_valid(new_piece):
                        self.current_piece = new_piece
                if self.movement[" "] == 1:
                    self.move_piece_down("hard")
        elif self.movement[" "] == 1:
            self.ready_for_game = not self.ready_for_game

    def piece_location_valid(self, custom_piece=None):
        piece = self.current_piece
        if custom_piece:
            piece = custom_piece
        for x in range(0, 4):
            for y in range(0, 4):
                has_piece = piece.shape[y][x]
                if has_piece and piece.x + x < 0:
                    return False
                if has_piece and piece.x + x > 9:
                    return False
                if has_piece and piece.y + y > 19:
                    return False
                try:
                    has_block = self.rows[piece.y + y].blocks[piece.x + x]
                    if has_piece and has_block:
                        return False
                except IndexError:
                    pass
        return True

    def move_piece_down(self, method="regular"):
        # method can be:
        # regular - for automatic falling
        # soft - for scoring 20 points per line while soft-dropping using 's'
        # hard- for instantly dropping a piece for 40 points per line using 'w'
        new_piece = self.current_piece.move("down")
        if self.piece_location_valid(new_piece):
            self.current_piece = new_piece
            if method == "hard":
                self.score += 2
                self.move_piece_down("hard")
            if method == "soft":
                self.score += 1
        else:
            for x in range(0, 4):
                for y in range(0, 4):
                    piece_color = self.current_piece.shape[y][x]
                    if piece_color:
                        self.rows[self.current_piece.y + y].blocks[
                            self.current_piece.x + x] = piece_color
            self.generate_new_piece()

    def update(self):
        # do recursive movements
        if self.movement["s"]:
            self.move_piece_down("soft")
        if self.movement["a"] > 3:
            new_piece = self.current_piece.move("left")
            if self.piece_location_valid(new_piece):
                self.current_piece = new_piece
        if self.movement["d"] > 3:
            new_piece = self.current_piece.move("right")
            if self.piece_location_valid(new_piece):
                self.current_piece = new_piece
        # remove full rows and update score
        lines_cleared = len([row for row in self.rows if row.is_full()])
        for row in self.rows:
            if row.is_full():
                self.rows.remove(row)
        line_scoring = {"1": 2, "2": 5, "3": 10, "4": 40}
        self.score += line_scoring.get(str(lines_cleared), 0)
        while len(self.rows) < 20:
            self.rows.insert(0, Row())
        # check if dead yet
        if any(self.rows[2].blocks):
            self.is_alive = False
            for row in self.rows:
                row.blocks = [GREY if block else None for block in row.blocks]

    def draw(self, pixels):
        if self.in_game:
            if self.player:
                # draw rows
                overlap_buffer(pixels, [row.pixels()
                               for row in self.rows], self.x, 12)
                if self.score >= 1000:
                    pixels[1][self.x] = RED
                    pixels[2][self.x] = RED
                    pixels[3][self.x] = RED
                    pixels[4][self.x] = RED
                    pixels[5][self.x] = RED
                try:
                    overlap_text(
                        pixels, str(self.score)[-3],
                        self.x+1, 1, [255, 255, 255])
                except IndexError:
                    pass
                try:
                    overlap_text(
                        pixels, str(self.score)[-2],
                        self.x+4, 1, [200, 200, 200])
                except IndexError:
                    pass
                overlap_text(
                    pixels, str(self.score - 1)[-1],
                    self.x+7, 1, [150, 150, 150])
            if self.is_alive and self.player:
                # draw piece
                overlap_buffer(pixels, self.next_piece.shape, self.x, 7)
                overlap_buffer(
                    pixels, self.current_piece.shape,
                    self.current_piece.x + self.x,
                    self.current_piece.y + 12)
            if not self.is_alive:
                overlap_text(pixels, "X", self.x + 4, 16, RED)
        else:
            color = WHITE
            if self.player and self.ready_for_game:
                color = GREEN
            elif self.player:
                color = BLUE
            overlap_text(pixels, "p", self.x + 1, 16, color)
            overlap_text(pixels, str(self.index+1), self.x + 6, 16, color)
        # draw right border
        overlap_buffer(pixels, [[WHITE]] * 20, self.x + 10, 12)
        for row in self.rows:
            if row.is_full():
                self.rows.remove(row)


class Row:
    def __init__(self):
        self.blocks = [None] * 10

    def is_full(self):
        return all(self.blocks)

    def pixels(self):
        return [block if block else BLACK for block in self.blocks]


class Piece:
    def __init__(self, shape, x=3, y=0):
        self.shape_name = shape
        self.shape = SHAPES[shape]
        self.x = x
        self.y = y
        for row in self.shape:
            if len(row) < 4:
                row.insert(0, None)
            while len(row) < 4:
                row.append(None)
        if len(self.shape) < 4:
            self.shape.insert(0, [None, None, None, None])
        while len(self.shape) < 4:
            self.shape.append([None, None, None, None])

    def move(self, direction):
        new_piece = Piece(self.shape_name, self.x, self.y)
        new_piece.shape = self.shape
        if direction == "down":
            new_piece.y += 1
        if direction == "right":
            new_piece.x += 1
        elif direction == "left":
            new_piece.x -= 1
        return new_piece

    def rotate(self, clockwise=True):
        new_piece = Piece(self.shape_name, self.x, self.y)
        new_piece.shape = self.shape
        if clockwise:
            new_piece.shape = [
                list(elem) for elem in list(zip(*self.shape[::-1]))]
        else:
            new_piece.shape = [
                list(elem) for elem in list(zip(*self.shape))[::-1]]
        return new_piece


class State(BaseState):
    name = "tetris"
    index = 8
    delay = 30
    game = None
    source = ""

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
                # create a black empty set of pixels
                pixels = []
                for _ in range(32):
                    pixels.append([])
                    for _ in range(96):
                        pixels[-1].append(BLACK)
                # main game loop
                self.game.update()
                # draw all elements
                if self.game:
                    self.game.draw(pixels)
                # flatten, convert and write buffer to display
                self.output_frame(bytes(self.flatten(pixels)))
                if not self.on_pi:
                    time_end = time()
                    time_delta = time_start - time_end
                    sleep(max(0.04-time_delta, 0))

    def receive(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            s.bind(("0.0.0.0", 7777))
            s.listen()
            while not self.killed:
                conn, addr = s.accept()
                threading.Thread(target=self.msg, args=(conn, addr)).start()

    def msg(self, conn, _addr):
        while not self.killed:
            data = b''
            try:
                data = conn.recv(6)
                conn.send(b"_")
            except Exception:
                index, board = next(((i, board) for (i, board) in enumerate(
                    self.game.boards) if board.player is conn), None)
                if board:
                    self.game.boards[index] = Board(index)
                filled_boards = [
                    board for board in self.game.boards if board.player
                ]
                if not filled_boards:
                    self.game = None
                break
            if not self.game:
                self.game = Game()
            board = next((board for board in self.game.boards if board.player is conn), None)
            request = data.decode().strip()
            if board and request:
                board.process_movement(request)
            elif request:
                empty_board = [
                    board for board in self.game.boards if not board.player]
                empty_board = next(
                    (board for board in self.game.boards if not board.player), None)
                if empty_board:
                    empty_board.player = conn
