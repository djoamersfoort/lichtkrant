#!/usr/bin/env bash
set -x
python3 index.py $@ | ./ledcat --geometry 96x32 rpi-led-matrix --led-cols 32 --led-rows 16 --led-chain 3 --led-parallel 2 --led-pwm-bits 8 --led-pwm-lsb-nanoseconds 500 --led-scan-mode progressive