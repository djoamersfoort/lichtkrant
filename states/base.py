from abc import abstractmethod
from shutil import which
from sys import stdout
from threading import Thread
from typing import List

from PIL import Image


class BaseState(Thread):
    name = "base"
    delay = 10
    index = 0

    def __init__(self):
        super().__init__()
        self.killed = False
        self.on_pi = which("rpi-update")
        self.player_class = None
        self.game_meta = None
        self.font_path = "./static/fonts/NotoMono-Regular.ttf"

    def kill(self) -> None:
        self.killed = True

    @abstractmethod
    def check(self, space_state: dict) -> bool:
        return True

    def add_player(self, _player: "BasePlayer"):
        pass

    def output_image(self, pil_image: Image) -> None:
        stdout.buffer.write(pil_image.tobytes())

    def output_frame(self, frame: bytes) -> None:
        stdout.buffer.write(frame)

    @staticmethod
    def text(text: str) -> List[List[int]]:
        chars = {
            "0": [[0, 1, 0], [1, 0, 1], [1, 0, 1], [1, 0, 1], [0, 1, 0]],
            "1": [[0, 1, 0], [1, 1, 0], [0, 1, 0], [0, 1, 0], [1, 1, 1]],
            "2": [[1, 1, 1], [0, 0, 1], [1, 1, 1], [1, 0, 0], [1, 1, 1]],
            "3": [[1, 1, 1], [0, 0, 1], [1, 1, 1], [0, 0, 1], [1, 1, 1]],
            "4": [[1, 0, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1], [0, 0, 1]],
            "5": [[1, 1, 1], [1, 0, 0], [1, 1, 1], [0, 0, 1], [1, 1, 1]],
            "6": [[1, 1, 1], [1, 0, 0], [1, 1, 1], [1, 0, 1], [1, 1, 1]],
            "7": [[1, 1, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1]],
            "8": [[1, 1, 1], [1, 0, 1], [1, 1, 1], [1, 0, 1], [1, 1, 1]],
            "9": [[1, 1, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1], [1, 1, 1]],
            "a": [[0, 1, 0], [1, 0, 1], [1, 1, 1], [1, 0, 1], [1, 0, 1]],
            "b": [[1, 1, 0], [1, 0, 1], [1, 1, 0], [1, 0, 1], [1, 1, 0]],
            "c": [[1, 1, 1], [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 1, 1]],
            "d": [[1, 1, 0], [1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 1, 0]],
            "e": [[1, 1, 1], [1, 0, 0], [1, 1, 0], [1, 0, 0], [1, 1, 1]],
            "f": [[1, 1, 1], [1, 0, 0], [1, 1, 0], [1, 0, 0], [1, 0, 0]],
            "g": [[0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 0, 1], [0, 1, 1]],
            "h": [[1, 0, 1], [1, 0, 1], [1, 1, 1], [1, 0, 1], [1, 0, 1]],
            "i": [[1, 1, 1], [0, 1, 0], [0, 1, 0], [0, 1, 0], [1, 1, 1]],
            "j": [[0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1], [1, 1, 1]],
            "k": [[1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 1], [1, 0, 1]],
            "l": [[1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 1, 1]],
            "m": [[1, 0, 1], [1, 1, 1], [1, 1, 1], [1, 0, 1], [1, 0, 1]],
            "n": [[1, 1, 0], [1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1]],
            "o": [[1, 1, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 1, 1]],
            "p": [[1, 1, 1], [1, 0, 1], [1, 1, 1], [1, 0, 0], [1, 0, 0]],
            "q": [[1, 1, 1], [1, 0, 1], [1, 0, 1], [1, 1, 0], [0, 0, 1]],
            "r": [[1, 1, 0], [1, 0, 1], [1, 1, 0], [1, 0, 1], [1, 0, 1]],
            "s": [[0, 1, 1], [1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0]],
            "t": [[1, 1, 1], [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0]],
            "u": [[1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 1, 1]],
            "v": [[1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1], [0, 1, 0]],
            "w": [[1, 0, 1], [1, 0, 1], [1, 1, 1], [1, 1, 1], [1, 0, 1]],
            "x": [[1, 0, 1], [1, 0, 1], [0, 1, 0], [1, 0, 1], [1, 0, 1]],
            "y": [[1, 0, 1], [1, 0, 1], [0, 1, 1], [0, 0, 1], [0, 1, 0]],
            "z": [[1, 1, 1], [0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 1, 1]],
            " ": [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
            ".": [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 1, 0]],
            "!": [[0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 0, 0], [0, 1, 0]]
        }
        buffer = [[], [], [], [], []]
        for char_index, char_text in enumerate(text):
            char_buffer = chars.get(
                str(char_text.lower()), [[], [], [], [], []])
            for row_index in range(0, 5):
                buffer[row_index].extend(char_buffer[row_index])
                if char_index < len(text) - 1:
                    buffer[row_index].append(0)
        return buffer

    def flatten(self, _list: List) -> List:
        if _list == []:
            return _list
        if isinstance(_list[0], list):
            return self.flatten(_list[0]) + self.flatten(_list[1:])
        return _list[:1] + self.flatten(_list[1:])
