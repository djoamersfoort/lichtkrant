from PIL import Image
from time import sleep
from sys import stdout

# module information
name = "nyan"
index = 0
delay = 12


# check function
def check(_state):
    return True


def get_image(path):
    image = Image.open(path)
    image.resize((96, 32))

    sequence = []

    try:
        while True:
            temp = image.copy()
            sequence.append(temp.convert('RGB'))
            image.seek(len(sequence))
    except EOFError:
        pass

    return sequence


# module runner
def run(_state):
    sequence = get_image('static/nyan.gif')

    while True:
        for frame in sequence:
            stdout.buffer.write(frame.tobytes())
            sleep(0.05)
