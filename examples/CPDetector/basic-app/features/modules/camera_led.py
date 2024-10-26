import logging

import faicons as fa
from shiny import render, reactive

from features.modules.camera import Camera


class CameraLed:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logging.debug("Initiate camera led instance.")
            cls._instance = super(CameraLed, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def values():
        camera = Camera()

        @render.ui
        def camera_led_update():
            reactive.invalidate_later(1)
            if camera.running:
                return fa.icon_svg(name="circle", fill="deepskyblue")
            elif camera.camera_connection:
                return fa.icon_svg(name="circle", fill="green")
            else:
                return fa.icon_svg(name="circle", fill="red")
