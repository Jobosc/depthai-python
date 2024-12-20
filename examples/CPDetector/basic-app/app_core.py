"""
This script initializes and runs a Gait Recording GUI application.

The application uses the Shiny framework to create a user interface for recording gait data.
It sets up various UI components, initializes logging, and handles camera operations in a separate thread.

Usage:
    Run this script to start the Gait Recording GUI application.
"""
import asyncio
import os
import threading

from shiny import ui, App, Inputs, Outputs, Session

from features.interface.card_values import CardValues
from features.interface.modal_remover import ModalRemover
from features.interface.session_manager import SessionManager
from features.interface.sidebar_buttons import SidebarButtons
from features.modules.camera import Camera
from features.modules.camera_led import CameraLed
from features.modules.recording_led import RecordLed
from features.modules.timestamps import Timestamps
from features.reactivity.buttons_controller import ButtonsController
from features.reactivity.metadata_controller import MetadataController
from features.reactivity.storage_controller import StorageController
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
            asyncio.run(camera.run(timestamps=timestamps))


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
    RecordLed.state()
    SidebarButtons()
    CardValues()
    ModalRemover(input)
    MetadataController(input, timestamps)
    ButtonsController(input, camera, timestamps)
    StorageController(input)
    SessionManager(input)

    # Setup Threading
    thread = threading.Thread(target=camera_handler)
    thread.start()


app = App(app_ui, server, static_assets={f"/{env.temp_path}": os.path.join(env.main_path, env.temp_path)})

# Save files from any day. Not just today
