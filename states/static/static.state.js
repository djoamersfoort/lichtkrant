const {join} = require("path");

module.exports = {
  name: "static",
  index: 0,
  check: false,
  module: join(__dirname, "static.js")
};
