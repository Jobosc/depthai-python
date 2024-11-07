"""
This script initializes and runs a Gait Recording GUI application.

The application uses the Shiny framework to create a user interface for recording gait data.
It sets up various UI components, initializes logging, and handles camera operations in a separate thread.

Usage:
    Run this script to start the Gait Recording GUI application.
"""

import os
import threading

from shiny import ui, App, Inputs, Outputs, Session

import features.interface.notification_modal as modals
import features.interface.session_view as session_view
import features.interface.sidebar_buttons as missing_data
import features.interface.sidebar_card as card_sidebar
import features.interface.text_fields as card_data
import features.reactivity.buttons as buttons
import features.reactivity.dataset as dataset
import features.reactivity.metadata as metadata
from features.modules.camera import Camera
from features.modules.camera_led import CameraLed
from features.modules.timestamps import Timestamps
from features.view import side_view, main_view, header
from utils.custom_logger import initialize_logger
from utils.parser import ENVParser

# Light Barrier code
camera = Camera()
timestamps = Timestamps()
env = ENVParser()

app_ui = ui.page_sidebar(
    ui.sidebar(side_view()),
    header(),
    main_view(),
    title="Gait Recording",
    window_title="Gait Recording GUI",
)


def camera_handler():
    """
    Handles the camera thread.

    Continuously checks if the camera is ready and not running, and if so, starts the camera with the provided timestamps.
    """
    while True:
        if camera.ready and not camera.running:
            camera.run(timestamps=timestamps)


def server(input: Inputs, output: Outputs, session: Session):
    """
    Handles the server side of the application.

    Initializes the logger, sets up various UI components and editors, and starts the camera handler thread.

    Args:
        input (Inputs): The input object for the server.
        output (Outputs): The output object for the server.
        session (Session): The session object for the server.
    """
    initialize_logger()
    CameraLed.state()
    missing_data.editor()
    card_data.values()
    modals.update(input)
    metadata.editor(input, timestamps)
    buttons.editor(input, camera, timestamps)
    dataset.editor(input)
    session_view.editor(input)
    card_sidebar.metadata(input)

    # Setup Threading
    thread = threading.Thread(target=camera_handler)
    thread.start()


app = App(app_ui, server, static_assets={f"/{env.temp_path}": os.path.join(env.main_path, env.temp_path)})