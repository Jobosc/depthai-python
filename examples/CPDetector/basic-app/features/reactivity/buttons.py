import logging
from datetime import datetime

from shiny import ui, reactive

from features.file_operations.delete import delete_temporary_recordings
from features.modules.camera import Camera
from features.modules.camera_led import CameraLed
from features.modules.timestamps import Timestamps
from features.reactivity.reactive_updates import UIState
from features.reactivity.reactive_values import save_view_state
from utils.parser import ENVParser

ui_state = UIState()


def editor(input, camera: Camera, timestamps: Timestamps):
    record_button_state = reactive.Value(False)

    @reactive.Effect
    @reactive.event(input.record_button)
    def update_record_button():
        if ui_state.unsaved_days:
            logging.info(
                "Record Button: Previous session(s) still exist that need to be completed before recording can start.")
            ui.notification_show(
                "You need to complete a previous session before you can start recording again!",
                duration=None,
                type="warning",
            )
        elif camera.camera_connection is False and record_button_state.get() is False:
            logging.info("Record Button: Camera is not connected and can therefore recording can't be started.")
            CameraLed.missing()
            ui.notification_show(
                "Please check if the camera is connected before starting the recording!",
                duration=None,
                type="warning",
            )
        else:
            CameraLed.available()
            if record_button_state.get() is True:
                logging.info("Record Button: Recording has been stopped.")
                record_button_state.set(False)
                camera.ready = False
                ui.update_action_button("record_button", label="Activate recording")
                ui_state.update_ui()
            else:
                logging.info("Record Button: Recording has been started.")
                timestamps.start_recording()
                record_button_state.set(True)
                camera.ready = True
                ui.update_action_button("record_button", label="Deactivate recording")
                ui_state.update_ui()

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
    @reactive.event(input.switch_mode)
    def change_pipeline_mode():
        camera.mode = input.switch_mode()
        if camera.mode:
            logging.info("Switch Button: Record mode has been activated.")
        else:
            logging.info("Switch Button: View mode has been activated.")

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
        delete_temporary_recordings()
        ui_state.update_ui()
