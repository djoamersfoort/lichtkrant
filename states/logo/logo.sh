#!/usr/bin/env bash

while true; do
  convert $1 -resize 128x32! -depth 8 RGB:-
  sleep 0.5
done
