import faicons as fa
from shiny import render, reactive

from features.reactivity.reactive_values import camera_led
import logging

STATUS = {
    "available": fa.icon_svg(name="circle", fill="green"),
    "missing": fa.icon_svg(name="circle", fill="red"),
    "recording": fa.icon_svg(name="circle", fill="deepskyblue"),
}


class CameraLed:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logging.debug("Initiate camera led instance.")
            cls._instance = super(CameraLed, cls).__new__(cls)
        return cls._instance

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