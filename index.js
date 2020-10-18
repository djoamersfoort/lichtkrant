// parsing the command-line arguments

const {ArgumentParser} = require("argparse");
const Runner = require("./runner.js");

const fs = require("fs");
const path = require("path");
const os = require("os");

let states = [];
let currentState = null;
let currentRunner = null;

const parser = new ArgumentParser({
  description: "A driver for the DJO Lichtkrant project."
});

parser.add_argument("-i", "--interval", {type: "int", default: 5000, help: "the interval at which states update"});
parser.add_argument("-s", "--state-dir", {type: "str", default: path.join(__dirname, "states"), help: "path to the states directory"});
parser.add_argument("-e", "--allow-empty", {action: "store_true", help: "allow an empty screen (no active state)"});

args = parser.parse_args();

// loading modules/states

fs.readdirSync(args.state_dir).forEach(state => {
  const absPath = path.join(args.state_dir, state, "index.js");
  if(!fs.existsSync(absPath)) return;

  const stateModule = require(absPath);
  if(states.map(s => s.name).indexOf(stateModule.name) !== -1) throw new Error(`Duplicate state name: '${stateModule.name}'!`);

  states.push(stateModule);
});

// update states

function update() {
  const sorted = states.filter(s => typeof s === "function" ? s() : s).sort((a, b) => b.index - a.index);
  const newState = sorted[0] || null;

  if(currentState === null || newState !== currentState) {
    if(currentRunner !== null) {
      currentRunner.stop();
    }

    if(newState !== null) {
      currentRunner = new Runner(newState);
      currentState = newState;
      currentRunner.run();
    } else if(args.allow_empty) {
      currentRunner = null;
      currentState = null;
    } else {
      throw new Error("There is no active state.");
    }
  }
}

update();
setInterval(update, args.interval);
