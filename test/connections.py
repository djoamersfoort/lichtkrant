import RPi.GPIO as io
io.setmode(io.BCM)

pins = [7,11,12,13,15,16,18,19,21,23,24,26]

for pin in pins:
    print("testing pin " + pin)
