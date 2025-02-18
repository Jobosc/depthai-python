"""
This module provides functionality to manage the light barrier sensor.

It defines the LightBarrier class which handles the initialization and state management of the light barrier sensor.

Classes:
    LightBarrier: Manages the light barrier sensor operations including initialization and state checking.
"""

import logging
import platform

if platform.system() == "Linux":
    from gpiozero import Button, Device
    from gpiozero.pins.lgpio import LGPIOFactory


class LightBarrier:
    """
    Manages the light barrier sensor operations including initialization and state checking.

    Attributes:
        _instance (LightBarrier): Singleton instance of the LightBarrier class.
        button (Button): The GPIO button instance for the light barrier sensor.
        gpio_exist (bool): Indicates if the GPIO button exists on the system.
    """
    _instance = None
    button = None
    gpio_exist = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LightBarrier, cls).__new__(cls)
            logging.debug("Initiate Light Barrier instance.")
            if platform.system() == "Linux":
                Device.pin_factory = LGPIOFactory()
                cls.button = Button(4, pull_up=False)
                cls.gpio_exist = True
        return cls._instance

    @property
    def activated(self):
        """
        Checks if the light barrier sensor is activated.

        Returns:
            bool: True if the light barrier sensor is activated, False otherwise.
        """
        if self.gpio_exist:
            return self.button.value
        else:
            return False
