from datetime import datetime

from shiny import ui, reactive

from features.functions import delete_session_on_date_folder, delete_temporary_folder
from features.interface.camera_led import CameraLed
from features.modules.camera import Camera
from features.modules.timestamps import Timestamps
from features.reactivity.reactive_updates import update_ui
from features.reactivity.reactive_values import record_button_state, save_view_state, unsaved_days
from utils.parser import ENVParser


def editor(input, camera: Camera, timestamps: Timestamps):
    @reactive.Effect
    @reactive.event(input.record_button)
    def update_record_button():
        if unsaved_days.get():
            ui.notification_show(
                f"You need to complete the session from a previous day before you can start recording again!",
                duration=None,
                type="warning",
            )
        elif camera.camera_connection is False and record_button_state.get() is False:
            CameraLed.missing()
            ui.notification_show(
                f"Please check if the camera is connected before starting the recording!",
                duration=None,
                type="warning",
            )
        else:
            CameraLed.available()
            if record_button_state.get() is True:
                record_button_state.set(False)
                camera.ready = False
                ui.update_action_button("record_button", label="Activate recording")
                update_ui()
            else:
                print(f"Activate recording: {datetime.now()}")
                timestamps.start_recording()
                record_button_state.set(True)
                camera.ready = True
                ui.update_action_button("record_button", label="Deactivate recording")
                update_ui()

    @reactive.Effect
    @reactive.event(input.save_button)
    def initiate_save():
        env = ENVParser()
        day = ""
        if input.rb_unsaved_days.is_set():
            date = datetime.strptime(
                input.rb_unsaved_days(), env.date_format
            ).strftime("%Y-%m-%d")
            day = f", from {date}"
        notification = ui.modal(
            ui.markdown(f"**Do you really want to save the recorded sessions{day}?**"),
            ui.input_action_button("save_yes", "✔ Yes", class_="btn-success"),
            ui.input_action_button("save_no", "✘ No", class_="btn-danger"),
            easy_close=False,
            footer=None,
        )
        ui.modal_show(notification)

    @reactive.Effect
    @reactive.event(input.delete_yes)
    def delete_session_for_specific_day():
        env = ENVParser()
        print(input.rb_unsaved_days())
        state = delete_session_on_date_folder(day=input.rb_unsaved_days())
        day = datetime.strptime(input.rb_unsaved_days(), env.date_format).strftime(
            "%Y-%m-%d"
        )
        if state:
            ui.notification_show(
                f"Dataset deletion from '{day}' was successful.",
                duration=None,
                type="default",
            )
            ui.update_radio_buttons("rb_unsaved_days")
        else:
            ui.notification_show(
                f"Deleting the dataset from '{day}', failed!",
                duration=None,
                type="error",
            )
        update_ui()

    @reactive.Effect
    @reactive.event(input.switch_mode)
    def change_pipeline_mode():
        camera.mode = input.switch_mode()

    """@reactive.Effect
    @reactive.event(input.convert_dataset)
    def initiate_conversion():
        notification = ui.modal(
            ui.markdown(
                f"**Do you really want to convert the videos of the selected dataset? WARNING: This is a time consuming task and should not run while recording patients.**"),
            ui.input_action_button("convert_yes", "✔ Yes", class_="btn-success"),
            ui.input_action_button("convert_no", "✘ No", class_="btn-danger"),
            easy_close=False,
            footer=None,
        )
        ui.modal_show(notification)"""

    @reactive.Effect
    @reactive.event(input.delete_dataset)
    def initiate_deletion():
        notification = ui.modal(
            ui.markdown(f"**Are you sure you want to delete selected datasets?**"),
            ui.input_action_button("delete_session_yes", "✔ Yes", class_="btn-success"),
            ui.input_action_button("delete_session_no", "✘ No", class_="btn-danger"),
            easy_close=False,
            footer=None,
        )
        ui.modal_show(notification)

    @reactive.Effect
    @reactive.event(input.delete_current_session_button)
    def initiate_delete_current_session():
        notification = ui.modal(
            ui.markdown(f"**Are you sure you want to delete selected the current session?**"),
            ui.input_action_button("delete_current_session_yes", "✔ Yes", class_="btn-success"),
            ui.input_action_button("delete_current_session_no", "✘ No", class_="btn-danger"),
            easy_close=False,
            footer=None,
        )
        ui.modal_show(notification)

    @reactive.Effect
    @reactive.event(input.cancel_edit_metadata_button)
    def cancel_edit_metadata():
        save_view_state.set(False)

    @reactive.Effect
    @reactive.event(input.delete_current_session_yes)
    def delete_current_session():
        delete_temporary_folder()
        update_ui()
