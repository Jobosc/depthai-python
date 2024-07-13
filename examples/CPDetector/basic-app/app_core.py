from shiny import ui, App, Inputs, Outputs, Session

import features.reactive_card_sidebar as card_sidebar
import features.reactive_modals as modals
import features.reactive_session_editor as session_editor
import features.reactive_session_recording as session_recording
import features.reactive_text as card_data
import features.reactive_ui as missing_data
from features.view import side_view, main_view, header

app_ui = ui.page_sidebar(ui.sidebar(side_view()), header(), main_view(), title="Gait Recording",
                         window_title="Gait Recording GUI")


def server(input: Inputs, output: Outputs, session: Session):
    missing_data.values()
    card_data.values()
    modals.values(input)
    session_recording.value(input)
    session_editor.values(input, output)
    card_sidebar.value(input, output)


app = App(app_ui, server)

# "- (Check if it is possible to show 'Stop recording' button)"
# "- (Add debug mode on second page, for settings)"
# "- (Add switch to switch between normal video and depth camera)"
# "- (Prevent code from starting if external hard drive is not connected)"
# Find out why video recording crashes after some time
# UI fixes
