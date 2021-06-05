# lichtkrant
A Chinese Hub75 LED panel reincarnated as a fancy marquee used at DJO.

## Installation
```bash
# clone the git repo
git clone https://github.com/djoamersfoort/lichtkrant
cd lichtkrant

# automatic installation for a new device
# this will create a systemctl service!
chmod +x *.sh
./setup.sh
```

## Usage
```
usage: index.py [-h] [-m MODULE] [-s STATE_DIR] [-r RECURSIVE] [-d] [-o]

A driver for the DJO Lichtkrant project.

optional arguments:
  -h, --help            show this help message and exit
  -m MODULE, --module MODULE
                        load a specific module by name
  -s STATE_DIR, --state-dir STATE_DIR
                        path to the states directory
  -r RECURSIVE, --recursive RECURSIVE
                        whether to search recursively
  -d, --dry             do not spew out pixel data
  -o, --offline         disable MQTT connectivity
```

Since the display makes use of the protocol Hub75, [ledcat](https://github.com/polyfloyd/ledcat) will be used.
Conveniently, ledcat also has a previewing option which prints the display in your terminal, since I'm not too fond of carrying around a bulky led panel.

```bash
# use preview mode for testing purposes
./debug.sh # [extra arguments]

# driving the display using rpi-led-matrix
./run.sh # [extra arguments]

# see run.py for a 'finetuned' configuration
```

## State Modules

The system works based on state modules. These are Python files ending in `.mod.py`

An example state file:
```python
import sys
from time import sleep
from states.base import BaseState

# The state class must be called 'State' and extend BaseState for things to work
class State(BaseState):
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
    def check(self, states):
        return states['djo'] is False

    # a function that is called when running the module
    # in this case it just fills the screen with white
    def run(self):
        while not self.killed:
            sys.stdout.buffer.write(bytes([0xFF] * 3072))

        sleep(1)
```

By default, all state files are included, even in subdirectories. If you don't want this, set the flag `-r, --recursive` to false.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
