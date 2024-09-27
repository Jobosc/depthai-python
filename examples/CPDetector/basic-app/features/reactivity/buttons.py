import asyncio
import datetime
import os
from features.modules.camera import Camera
from shiny import ui, reactive

from features.functions import (
    store_participant_metadata,
    get_files_to_move,
    move_data_from_temp_to_main_storage,
    temp_path,
    main_path,
    date_format,
)
from features.modules.participant import Participant
from features.reactive_updates import update_ui
from features.reactive_values import save_view_state, camera_state, record_button_state


def editor(input, camera: Camera):
    @reactive.Effect
    @reactive.event(input.record_button)
    def update_record_button():
        if input.unsaved_days.is_set():
            ui.notification_show(
                f"You need to complete the session from a previous day before you can start recording again!",
                duration=None,
                type="warning",
            )
        elif camera_state.get() is False and record_button_state.get() is False:
            ui.notification_show(
                f"Please check if the camera is connected before starting the recording!",
                duration=None,
                type="warning",
            )
        else:
            if record_button_state.get() is True:
                record_button_state.set(False)
                camera.ready = False
                ui.update_action_button("record_button", label="Activate recording")
            else:
                record_button_state.set(True)
                camera.ready = True
                ui.update_action_button("record_button", label="Deactivate recording")

    @reactive.Effect
    @reactive.event(input.save_button)
    def initiate_save():
        day = ""
        if input.rb_unsaved_days.is_set():
            date = datetime.datetime.strptime(
                input.rb_unsaved_days(), date_format
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

