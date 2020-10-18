module.exports = {
  name: "clock",
  index: 1,
  check: true,
  command: `
  while true; do
    convert -background black -fill green -font Courier -pointsize 24 -size 128x32 -gravity center -depth 8 caption:"$(date +%T)" RGB:-
    sleep 1;
  done
  `
};
