module.exports = {

  // give the state a name
  name: "example",

  // the state with the highest index is shown
  index: 0,

  // either a boolean or a function that returns a boolean
  // if the boolean is false the state won't be shown
  check: true,
  // check: () => Math.random() < 0.5,

  // the command that is ran when the module is enabled
  command: `perl -e 'while(1){print "\\xff\\xff\\xff" x ${128*32}}'`

};
