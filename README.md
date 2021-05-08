# lichtkrant
A Chinese Hub75 LED panel reincarnated as a fancy marquee used at DJO.

## Installation
```bash
# clone the git repo
git clone https://github.com/djoamersfoort/lichtkrant
cd lichtkrant

# use sudo because the systemd service runs as root
sudo pip install -r requirements.txt

# generate a systemd file
chmod +x *.sh
./migrate.sh
```

## Usage
```
usage: index.py [-h] [-i INTERVAL] [-m MODULE] [-s STATE_DIR] [-r RECURSIVE]

A driver for the DJO Lichtkrant project.

optional arguments:
  -h, --help            show this help message and exit
  -i INTERVAL, --interval INTERVAL
                        the delay in milliseconds between updates
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

# there is also a pre-configured script
python index.py | ./ledcat
```

## State Modules

The system works based on state modules. These are YAML files ending in `.yaml`

An example state file:
```yaml
# give the state a name
name: example

# the state with the highest index is shown
index: 0

# either a boolean or an eval string returning a boolean
# if the boolean is false the state won't be shown

# available arguments for the check eval function:
# states = {'djo':True/False,'bitlair':True/False}

check: true

# the command that is ran when the module is enabled
command: perl -e 'while(1){{print "\\x00\\x00\\xff" x 4096}}'

# a python module can also be passed instead of a command
# note that the path is relative to the index python file
# module: "text.py"
```

By default, all state files are included, even in subdirectories. If you don't want this, set the flag `-r, --recursive` to false.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
