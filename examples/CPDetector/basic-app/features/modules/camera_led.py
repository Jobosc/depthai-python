import logging

import faicons as fa
from shiny import render, reactive

camera_led = reactive.Value(None) #TODO: Try to remove

STATUS = {
    "available": fa.icon_svg(name="circle", fill="green"),
    "missing": fa.icon_svg(name="circle", fill="red"),
    "recording": fa.icon_svg(name="circle", fill="deepskyblue"),
}


class CameraLed:
    _instance = None
    __led_state = reactive.Value(None)

    def __new__(cls):
        if cls._instance is None:
            logging.debug("Initiate camera led instance.")
            cls._instance = super(CameraLed, cls).__new__(cls)
        return cls._instance

    @property
    def state(self):
        return self.__led_state.get()

    @state.setter
    def state(self, value):
        self.__led_state.set(value)

    @staticmethod
    def values():
        @render.ui
        @reactive.event(camera_led)
        def camera_led_update():
            logging.debug(f"Collect camera led state.")
            return camera_led.get()

    def record():
        @reactive.Effect
        def value():
            camera_led.set(STATUS["recording"])

    def available():
        @reactive.Effect
        def value():
            camera_led.set(STATUS["available"])

    def missing():
        @reactive.Effect
        def value():
            camera_led.set(STATUS["missing"])
