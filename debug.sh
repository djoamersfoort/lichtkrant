#!/usr/bin/env bash

python3.11 index.py -o --port 8080 $@ | ./ledcat --geometry 96x32 show
