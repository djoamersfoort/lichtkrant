#!/usr/bin/env bash

# add --color-correction srgb after ledcat for color correction
/home/pi/.cargo/bin/ledcat --geometry 128x32 rpi-led-matrix --led-cols 32 --led-rows 16 --led-chain 4 --led-parallel 2 --led-pwm-bits 8 --led-pwm-lsb-nanoseconds 500 --led-scan-mode progressive
