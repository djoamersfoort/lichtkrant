// parsing the command-line arguments

const {ArgumentParser} = require("argparse");

const fs = require("fs");
const path = require("path");
const os = require("os");

let states = [];
let current = null;

const parser = new ArgumentParser({
  description: "A driver for the DJO Lichtkrant project."
});

parser.add_argument("-i", "--interval", {type: "int", default: 5000, help: "the interval at which states update"});

args = parser.parse_args();

// loading modules/states

fs.readdirSync(path.join(__dirname, "states")).forEach(state => {
  if(!state.endsWith(".js") || state.startsWith("_")) return;

  const stateModule = require("./states/" + state);

  if(states.map(s => s.name).indexOf(stateModule.name) !== -1) throw new Error(`Duplicate state name: '${stateModule.name}'!`);

  states.push(stateModule);
});

// update states

function update() {
  states = states.filter(s => s.check).sort((a, b) => a.index - b.index);

  if(current === null || current.name !== states[0].name) {
    if(current !== null) {
      current.stop();
    }

    current = states[0];
    current.start();
  }
}

update();
setInterval(update, args.interval);
