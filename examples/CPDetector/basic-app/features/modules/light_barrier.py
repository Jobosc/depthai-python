from gpiozero import Button


class LightBarrier(object):
    _instance = None
    button = None

    def __new__(cls):
        if cls._instance is None:
            print("Creating the light barrier object")
            cls._instance = super(LightBarrier, cls).__new__(cls)
            cls.button = Button(4, pull_up=False)
        return cls._instance

    @property
    def activated(self):
        return self.button.value
