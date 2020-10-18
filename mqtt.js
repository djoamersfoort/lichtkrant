// get the bitlair mqtt state

const {connect} = require("mqtt");
const states = {djo: false, bitlair: false};

const client = connect("mqtt://bitlair.nl");

client.on("connect", () => {
  client.subscribe("bitlair/state");
  client.subscribe("bitlair/state/djo");
});

client.on("message", function(topic, message) {
  if(topic === "bitlair/state") {
    states.bitlair = message == "open";
  } else if(topic === "bitlair/state/djo") {
    states.djo = message == "open";
  }
});

module.exports = states;
