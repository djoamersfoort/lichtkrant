import sys
from time import sleep


# give the state a name
name = "example"

# the state with the highest index is shown
# if multiple states have the same index it will be randomly selected
index = 30

# delay in seconds to wait until the next update
delay = 60


# a function returning a boolean
# this decides if the module will be shown
# the spacestate is available as the first argument
def check(states):
    return states['djo'] is True


# run the module
def run():
    while True:
        for i in range(96 * 32):
            sys.stdout.buffer.write(bytes(0xFF00FF))

    sleep(0.05)
