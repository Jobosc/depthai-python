"""
This module handles the button operations for the application.

Classes:
    Buttons: Manages the button operations including recording, saving, switching modes, converting datasets, and deleting sessions.
"""

import logging
from datetime import datetime

from shiny import ui, reactive

from features.file_operations.delete import delete_temporary_recordings
from features.modules.camera import Camera
from features.modules.timestamps import Timestamps
from features.modules.ui_state import UIState
from utils.parser import ENVParser


class ButtonsController:
    input = None
    camera = None
    timestamps = None
    ui_state = UIState()
    record_button_state = reactive.Value(False)

    def __init__(self, input, camera: Camera, timestamps: Timestamps):
        """
        Initializes the Buttons with the given input, camera, and timestamps.

        Args:
            input: The input object for the server.
            camera (Camera): The camera object for the session.
            timestamps (Timestamps): The timestamps object for the session.
        """
        self.input = input
        self.camera = camera
        self.timestamps = timestamps
        self.ui_state = UIState()
        self.update_record_button()
        self.initiate_save()
        self.change_pipeline_mode()
        self.initiate_conversion()
        self.initiate_deletion()
        self.initiate_delete_current_session()
        self.cancel_edit_metadata()
        self.delete_current_session()

    def update_record_button(self):
        """
        Updates the record button state.

        Checks if there are unsaved sessions or if the camera is connected, and updates the record button state accordingly.
        """
        @reactive.Effect
        @reactive.event(self.input.record_button)
        def _():
            if self.ui_state.unsaved_days: # Check if there are unsaved sessions
                logging.info("Record Button: Previous session(s) still exist that need to be completed before recording can start.")
                ui.notification_show(
                    "You need to complete a previous session before you can start recording again!",
                    duration=None,
                    type="warning",
                )
            elif self.camera.camera_connection is False and self.record_button_state.get() is False:    # Check if the camera is connected
                logging.info("Record Button: Camera is not connected and therefore recording can't be started.")
                ui.notification_show(
                    "Please check if the camera is connected before starting the recording!",
                    duration=None,
                    type="warning",
                )
            else:   # Activate or Deactivate recording based on the current state
                if self.record_button_state.get() is True:
                    logging.info("Record Button: Recording has been stopped.")
                    self.record_button_state.set(False)
                    self.camera.ready = False
                    ui.update_action_button("record_button", label="Activate recording")
                    self.ui_state.update_ui()
                else:
                    logging.info("Record Button: Recording has been started.")
                    self.timestamps.start_recording()
                    self.record_button_state.set(True)
                    self.camera.ready = True
                    ui.update_action_button("record_button", label="Deactivate recording")
                    self.ui_state.update_ui()

    def initiate_save(self):
        """
        Initiates the save process.

        Displays a confirmation modal to save the recorded sessions.
        """
        @reactive.Effect
        @reactive.event(self.input.save_button)
        def _():
            env = ENVParser()
            day = ""
            if self.input.rb_unsaved_days.is_set():
                date = datetime.strptime(
                    self.input.rb_unsaved_days(), env.date_format
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

    def change_pipeline_mode(self):
        """
        Changes the pipeline mode.

        Updates the camera mode based on the input switch mode.
        """
        @reactive.Effect
        @reactive.event(self.input.switch_mode)
        def _():
            self.camera.mode = self.input.switch_mode()
            if self.camera.mode:
                logging.info("Switch Button: Record mode has been activated.")
            else:
                logging.info("Switch Button: View mode has been activated.")

    def initiate_conversion(self):
        """
        Initiates the conversion process.

        Displays a confirmation modal to convert the videos of the selected dataset.
        """
        @reactive.Effect
        @reactive.event(self.input.convert_dataset)
        def _():
            notification = ui.modal(
                ui.markdown(
                    f"**Do you really want to convert the videos of the selected dataset? WARNING: This is a time consuming task and should not run while recording patients.**"),
                ui.input_action_button("convert_yes", "✔ Yes", class_="btn-success"),
                ui.input_action_button("convert_no", "✘ No", class_="btn-danger"),
                easy_close=False,
                footer=None,
            )
            ui.modal_show(notification)

    def initiate_deletion(self):
        """
        Initiates the deletion process.

        Displays a confirmation modal to delete the selected datasets.
        """
        @reactive.Effect
        @reactive.event(self.input.delete_dataset)
        def _():
            notification = ui.modal(
                ui.markdown(f"**Are you sure you want to delete selected datasets?**"),
                ui.input_action_button("delete_session_yes", "✔ Yes", class_="btn-success"),
                ui.input_action_button("delete_session_no", "✘ No", class_="btn-danger"),
                easy_close=False,
                footer=None,
            )
            ui.modal_show(notification)

    def initiate_delete_current_session(self):
        """
        Initiates the deletion of the current session.

        Displays a confirmation modal to delete the current session.
        """
        @reactive.Effect
        @reactive.event(self.input.delete_current_session_button)
        def _():
            notification = ui.modal(
                ui.markdown(f"**Are you sure you want to delete the current session?**"),
                ui.input_action_button("delete_current_session_yes", "✔ Yes", class_="btn-success"),
                ui.input_action_button("delete_current_session_no", "✘ No", class_="btn-danger"),
                easy_close=False,
                footer=None,
            )
            ui.modal_show(notification)

    def cancel_edit_metadata(self):
        """
        Cancels the metadata editing process.

        Resets the save view state.
        """
        @reactive.Effect
        @reactive.event(self.input.cancel_edit_metadata_button)
        def _():
            self.ui_state.save_view_state = False

    def delete_current_session(self):
        """
        Deletes the current session.

        Deletes the temporary recordings and updates the UI.
        """
        @reactive.Effect
        @reactive.event(self.input.delete_current_session_yes)
        def _():
            delete_temporary_recordings()
            self.ui_state.update_ui()