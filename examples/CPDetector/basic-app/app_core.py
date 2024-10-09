import os
import threading

from shiny import ui, App, Inputs, Outputs, Session

from features.interface.camera_led import CameraLed
import features.interface.notification_modal as modals
import features.interface.session_view as session_view
import features.interface.sidebar_buttons as missing_data
import features.interface.sidebar_card as card_sidebar
import features.interface.text_fields as card_data
import features.reactivity.buttons as buttons
import features.reactivity.dataset as dataset
import features.reactivity.metadata as metadata
from features.modules.camera import Camera
from features.modules.light_barrier import LightBarrier
from features.view import side_view, main_view, header

# Light Barrier code
camera = Camera()
button = LightBarrier()

app_ui = ui.page_sidebar(
    ui.sidebar(side_view()),
    header(),
    main_view(),
    ui.tags.video(
        ui.tags.source(src="static/color.mp4", type="video/mp4"),
        controls=True,
        width="800px",
        autoplay=False
    ),
    title="Gait Recording",
    window_title="Gait Recording GUI",
)


def hw_button_handler():
    while True:
        if button.activated and not camera.running and camera.ready:
            print("Start camera after light barrier trigger.")
            camera.run()


def server(input: Inputs, output: Outputs, session: Session):
    CameraLed(input, output).values()
    missing_data.editor()
    card_data.values()
    modals.update(input)
    metadata.editor(input)
    buttons.editor(input, camera)
    dataset.editor(input)
    session_view.editor(input, output)
    card_sidebar.metadata(input, output)

    thread = threading.Thread(target=hw_button_handler)
    thread.start()

app = App(app_ui, server, static_assets={"/static": os.path.join(os.path.dirname(__file__), "static")})

# Check if there are files available to save before clicking save (left handside). If there aren't, a warning should appear
