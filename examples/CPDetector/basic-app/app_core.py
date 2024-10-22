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
from features.interface.camera_led import CameraLed
from features.modules.camera import Camera
from features.modules.timestamps import Timestamps
from features.view import side_view, main_view, header
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
    while True:
        if camera.ready and not camera.running:
            camera.run(timestamps=timestamps)


def server(input: Inputs, output: Outputs, session: Session):
    CameraLed(input, output).values()
    missing_data.editor()
    card_data.values()
    modals.update(input)
    metadata.editor(input, timestamps)
    buttons.editor(input, camera, timestamps)
    dataset.editor(input)
    session_view.editor(input, output)
    card_sidebar.metadata(input, output)

    thread = threading.Thread(target=camera_handler)
    thread.start()


app = App(app_ui, server, static_assets={f"/{env.temp_path}": os.path.join(env.main_path, env.temp_path)})

# Add Logging
