#!/usr/bin/env bash
export PYTHONUNBUFFERED=1
python3 index.py $@ | ./ledcat --geometry 96x32 show