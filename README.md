# lichtkrant
A Chinese Hub75 LED panel reincarnated as a fancy marquee used at DJO.

## Installation
```bash
# clone the git repo
git clone https://github.com/djoamersfoort/lichtkrant
cd lichtkrant

# automatic installation
chmod +x *.sh
./migrate.sh
```

## Usage
```
usage: index.py [-h] [-m MODULE] [-s STATE_DIR] [-r RECURSIVE]

A driver for the DJO Lichtkrant project.

optional arguments:
  -h, --help            show this help message and exit
  -m MODULE, --module MODULE
                        load a specific module by name
  -s STATE_DIR, --state-dir STATE_DIR
                        path to the states directory
  -r RECURSIVE, --recursive RECURSIVE
                        whether to search recursively
```

Since the display makes use of the protocol Hub75, [ledcat](https://github.com/polyfloyd/ledcat) will be used.
Conveniently, ledcat also has a previewing option which prints the display in your terminal, since I'm not too fond of carrying around a bulky led panel.

```bash
# use preview mode for testing purposes
python index.py | ledcat --geometry 128x32 show

# driving the display using rpi-led-matrix
python index.py | sudo ledcat --geometry 128x32 rpi-led-matrix --led-cols 32 --led-rows 16 --led-chain 4 --led-parallel 2
```

## State Modules

The system works based on state modules. These are Python files ending in `.mod.py`

An example state file:
```python
import sys
from time import sleep

# give the state a name
# this name should be unique!
name = "example"

# the state with the highest index is shown
# if multiple states have the same index it will be randomly selected
index = 0

# delay in seconds to wait until the next update
delay = 60


# this function decides if the module will be shown
# the check function must return a boolean
# the spacestate is available as the first argument
def check(states):
    return states['djo'] is False


# a function that is called when running the module
# in this case it just fills the screen with white
def run():
    while True:
        sys.stdout.buffer.write(bytes([0xFF] * 3072))

    sleep(0.05)
```

By default, all state files are included, even in subdirectories. If you don't want this, set the flag `-r, --recursive` to false.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
