import logging
import platform

if platform.system() == "Linux":
    from gpiozero import Button


class LightBarrier(object):
    _instance = None
    button = None
    gpio_exist = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LightBarrier, cls).__new__(cls)
            logging.debug("Initiate Light Barrier instance.")
            if platform.system() == "Linux":
                cls.button = Button(4, pull_up=False)
                cls.gpio_exist = True
        return cls._instance

    @property
    def activated(self):
        if self.gpio_exist:
            return self.button.value
        else:
            return False
