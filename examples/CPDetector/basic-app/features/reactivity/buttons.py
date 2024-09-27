import datetime

from shiny import ui, reactive

from features.functions import date_format
from features.modules.camera import Camera
from features.reactivity.reactive_updates import update_ui
from features.reactivity.reactive_values import camera_state, record_button_state


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

    @reactive.Effect
    @reactive.event(input.delete_yes)
    def delete_session_for_specific_day():
        print(input.rb_unsaved_days())
        state = delete_session_on_date_folder(day=input.rb_unsaved_days())
        day = datetime.datetime.strptime(input.rb_unsaved_days(), date_format).strftime(
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
