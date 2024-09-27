from time import sleep

from gpiozero import Button

button = Button(4, pull_up=False)

while True:
    if button.value:
        print(1)
    sleep(0.5)
