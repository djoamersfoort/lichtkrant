const {exec} = require("child_process");

module.exports = function(state) {
  this.name = state.name;
  this.command = state.command;

  this.run = () => {
    if(this.process) return;

    this.process = exec(this.command, {encoding: "raw"});
    this.process.stdout.pipe(process.stdout);
  };

  this.stop = () => {
    if(!this.process) return;

    this.process.kill();
    this.process = null;
  };
};
