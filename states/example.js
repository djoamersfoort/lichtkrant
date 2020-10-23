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
