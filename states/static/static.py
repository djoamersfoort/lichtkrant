import random

while True:
  print(bytes([random.randint(0, 255) for i in range(0, 128*32*3)]))
