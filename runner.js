const {exec, fork} = require("child_process");

module.exports = function(state) {
  this.name = state.name;

  if(state.command) this.command = state.command;
  if(state.module) this.module = state.module;

  this.run = () => {
    if(this.process) return;

    if(this.command) {
      this.process = exec(this.command, {encoding: "raw"});
    }

    if(this.module) {
      this.process = fork(this.module, {silent: true});
    }

    this.process.stdout.pipe(process.stdout);
    this.process.stderr.pipe(process.stderr);
  };

  this.stop = () => {
    if(!this.process) return;

    this.process.kill();
    this.process = null;
  };
};
