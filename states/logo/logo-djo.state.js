const {join} = require("path");

module.exports = {
  name: "djo",
  index: 1,
  check: state => state.djo,
  command: `${join(__dirname, "logo.sh")} ${join(__dirname, "djo.png")}`
};
