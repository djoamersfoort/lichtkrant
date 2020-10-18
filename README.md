# lichtkrant
A Chinese Hub75 LED panel reincarnated as a fancy marquee used at DJO.

## Installation
```bash
git clone https://github.com/djoamersfoort/lichtkrant
cd lichtkrant
npm install
```

## Usage
The help page of the command is as follows:
```
usage: index.js [-h] [-i INTERVAL] [-s STATE_DIR] [-m MODULE] [-r]

A driver for the DJO Lichtkrant project.

optional arguments:
  -h, --help            show this help message and exit
  -i INTERVAL, --interval INTERVAL
                        the interval at which states update
  -s STATE_DIR, --state-dir STATE_DIR
                        path to the states directory
  -m MODULE, --module MODULE
                        load a specific module by name
  -r, --no-recursive    disable recursive directory searching
```

To display to the screen, pipe the stdout to [ledcat](https://github.com/polyfloyd/ledcat).

```bash
# use show mode for testing purposes
node index.js | ledcat --geometry 128x32 show

# driving the display using rpi-led-matrix
node index.js | ledcat --geometry 128x32 rpi-led-matrix
```

## State Modules

The system works based on state modules. These are JavaScript files ending in `.state.js`

An example state file:
```js
module.exports = {

  // give the state a name
  name: "example",

  // the state with the highest index is shown
  index: 0,

  // either a boolean or a function that returns a boolean
  // if the boolean is false the state won't be shown
  check: false,
  // a SpaceState argument is passed to the function: {djo:true/false,bitlair:true/false}
  // check: states => states.djo,

  // the command that is ran when the module is enabled
  command: `perl -e 'while(1){print "\\x00\\x00\\xff" x ${128*32}}'`

  // a standalone file can also be ran
  // file: "test"

  // a javascript module can be passed instead of a command
  // module: "text.js"
};
```

By default, all state files are included, even in subdirectories. If you don't want this, use the flag `-r, --no-recursive`.
