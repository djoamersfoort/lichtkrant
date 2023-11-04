#!/usr/bin/env bash
export PYTHONUNBUFFERED=1
python3 index.py -o --port 8080 $@ | ./ledcat --geometry 96x32 show
