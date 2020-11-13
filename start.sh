#!/usr/bin/env bash

echo lichtkrant service running
cd /home/pi/lichtkrant
python3 index.py | ./ledcat.sh
