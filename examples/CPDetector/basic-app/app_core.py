from shiny import ui, App, Inputs, Outputs, Session

import features.reactive_card_sidebar as card_sidebar
import features.reactive_modals as modals
import features.reactive_session_editor as session_editor
import features.reactive_session_recording as session_recording
import features.reactive_text as card_data
import features.reactive_ui as missing_data
import features.modules.camera_led as cam_led
from features.view import side_view, main_view, header

from features.modules.camera import Camera
from features.modules.light_barrier import LightBarrier
import threading

# Light Barrier code
camera = Camera()
button = LightBarrier()

app_ui = ui.page_sidebar(
    ui.sidebar(side_view()),
    header(),
    main_view(),
    title="Gait Recording",
    window_title="Gait Recording GUI",
)


def hw_button_handler():
    while True:
        if button.activated and not camera.running and camera.ready:
            print("Start camera after light barrier trigger.")
            camera.run()


def server(input: Inputs, output: Outputs, session: Session):
    cam_led.values(camera)
    missing_data.values()
    card_data.values()
    modals.values(input)
    session_recording.value(input, camera)
    session_editor.values(input, output, camera)
    card_sidebar.value(input, output)

    thread = threading.Thread(target=hw_button_handler)
    thread.start()


app = App(app_ui, server)

# Check if there are files available to save before clicking save (left handside). If there aren't, a warning should appear