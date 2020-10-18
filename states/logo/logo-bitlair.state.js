const {join} = require("path");

module.exports = {
  name: "bitlair",
  index: 0,
  check: state => state.bitlair,
  command: `${join(__dirname, "logo.sh")} ${join(__dirname, "bitlair.jpg")}`
};
