"""
This module provides functionality to manage the camera LED status.

It defines the CameraLed class which handles the LED status updates based on the camera's state.

Classes:
    CameraLed: Manages the LED status updates for the camera.

Methods:
    state: Updates the LED status based on the camera's running state and connection status.
"""

import logging

import faicons as fa
from shiny import render, reactive

from features.modules.camera import Camera


class CameraLed:
    """
    Manages the LED status updates for the camera.

    Attributes:
        _instance (CameraLed): Singleton instance of the CameraLed class.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logging.debug("Initiate camera led instance.")
            cls._instance = super(CameraLed, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def state():
        """
        Updates the LED status based on the camera's running state and connection status.

        Returns:
            render.ui: The UI element representing the LED status.
        """
        camera = Camera()

        @render.ui
        def camera_led_update():
            reactive.invalidate_later(1)
            if camera.running and not camera.storing_data:
                return fa.icon_svg(name="circle", fill="deepskyblue")
            elif camera.camera_connection and not camera.storing_data:
                return fa.icon_svg(name="circle", fill="green")
            else:
                return fa.icon_svg(name="circle", fill="red")