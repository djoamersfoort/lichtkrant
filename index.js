// parsing the command-line arguments

const {ArgumentParser} = require("argparse");
const Runner = require("./runner.js");
const SpaceStates = require("./mqtt.js");

const fs = require("fs");
const path = require("path");
const os = require("os");

let states = [];
let currentState = null;
let currentRunner = null;

const parser = new ArgumentParser({
  description: "A driver for the DJO Lichtkrant project."
});

parser.add_argument("-i", "--interval", {type: "int", default: 2500, help: "the interval at which states update"});
parser.add_argument("-s", "--state-dir", {type: "str", default: path.join(__dirname, "states"), help: "path to the states directory"});
parser.add_argument("-m", "--module", {type: "str", default: null, help: "load a specific module by name"});
parser.add_argument("-r", "--no-recursive", {action: "store_true", help: "disable recursive directory searching"});

args = parser.parse_args();

// loading modules/states

function readDir(dir) {
  fs.readdirSync(dir).forEach(state => {
    const absPath = path.join(dir, state);

    if(fs.statSync(absPath).isDirectory() && !args.no_recursive) readDir(path.join(dir, state));
    if(!state.endsWith(".state.js")) return;

    const stateModule = require(absPath);

    if(states.map(s => s.name).indexOf(stateModule.name) !== -1) throw new Error(`Duplicate state name: '${stateModule.name}'!`);
    if(args.module !== null && stateModule.name !== args.module) return;

    states.push(stateModule);
  });
}

readDir(args.state_dir);

if(states.length === 0) {
  throw new Error(args.module !== null ? "No module found by that name." : "No states loaded.");
}

// update states

async function update() {
  const sorted = states.filter(s => typeof s.check === "function" ? s.check(SpaceStates) : s.check).sort((a, b) => b.index - a.index);

  let newState = sorted[0] || null;

  if(args.module !== null) newState = states[0];

  if(currentState === null || newState !== currentState) {
    if(currentRunner !== null) {
      currentRunner.stop();
    }

    if(newState !== null) {
      currentRunner = new Runner(newState);
      currentState = newState;
      currentRunner.run();
    } else {
      throw new Error("There is no active state.");
    }
  }
}

update();
setInterval(update, args.interval);
