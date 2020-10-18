const {Readable} = require("stream");
const {sleep} = require("../util.js");

let interval;

module.exports = {

  // give the state a name
  name: "example",

  // the state with the highest index is shown
  index: 0,

  // either a boolean or a function that returns a boolean
  // if the boolean is false the state won't be shown
  check: true,
  // this.check = () => Math.random() < 0.5;

  // a start function provided with the ledcat stdin
  start: function() {
    interval = setInterval(() => {
      process.stdout.write(Buffer.from("FF00FF".repeat(128*16), "hex"));
    }, 100);
  },

  // a cleanup function called when the state is stopped
  // make sure all writes to the stream are stopped or things go very bad very fast
  stop: function() {
    clearInterval(interval);
  }

};
