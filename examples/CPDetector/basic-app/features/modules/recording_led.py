"""
This module provides functionality to manage the recording session LED status.

It defines the RecordLed class which handles the LED status updates based on the record state.

Classes:
    RecordLed: Manages the LED status updates for the recording session.

Methods:
    state: Updates the LED status based on the recording session's running state and connection status.
"""

import logging

import faicons as fa
from shiny import render, reactive

from features.modules.camera import Camera
from features.modules.light_barrier import LightBarrier


class RecordLed:
    """
    Manages the LED status updates for the recording session.

    Attributes:
        _instance (RecordLed): Singleton instance of the RecordLed class.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logging.debug("Initiate record led instance.")
            cls._instance = super(RecordLed, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def state():
        """
        Updates the LED status based on the camera's running state and connection status.

        Returns:
            render.ui: The UI element representing the LED status.
        """
        camera = Camera()
        light_barrier = LightBarrier()

        @render.ui
        def recording_led_update():
            reactive.invalidate_later(1)
            if not camera.running:
                return fa.icon_svg(name="circle", fill="gray")
            elif light_barrier.activated:
                return fa.icon_svg(name="circle", fill="green")
            else:
                return fa.icon_svg(name="circle", fill="red")
