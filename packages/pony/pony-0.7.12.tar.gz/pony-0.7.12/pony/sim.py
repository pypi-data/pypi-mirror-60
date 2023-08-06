from random import randint
from time import sleep

value = 100.0

while True:
    print(value)
    if randint(0, 1):
        value = value * 1.5
    else:
        value = value * 0.6
    sleep(0.1)

