from gpiozero import Button
from time import sleep

button = Button(4, pull_up=False)

while True:
    if button.value:
        print(1)
    sleep(0.5)
