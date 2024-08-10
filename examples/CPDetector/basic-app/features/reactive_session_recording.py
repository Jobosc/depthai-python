import asyncio
import datetime
import os

from shiny import ui, reactive

from .functions import (
    store_participant_metadata,
    get_files_to_move,
    move_data_from_temp_to_main_storage,
    temp_path,
    main_path,
    date_format,
)
from .modules.participant import Participant
from .reactive_updates import update_ui
from .reactive_values import save_view_state, start_time, camera_state, hard_drive_state
from features.modules.camera import Camera


def value(input, camera):
    @reactive.Effect
    @reactive.event(input.record_button)
    def start_recording():
        if input.unsaved_days.is_set():
            ui.notification_show(
                f"You need to complete the session from a previous day before you can start recording again!",
                duration=None,
                type="warning",
            )
        elif camera_state.get() is False:
            ui.notification_show(
                f"Please check if the camera and hard drive are connected before starting the recording!",
                duration=None,
                type="warning",
            )
        else:

            start_time.set(datetime.datetime.now())
            camera.run(block=True)
            update_ui()

    @reactive.Effect
    @reactive.event(input.edit_metadata_button)
    def edit_metadata():
        person = Participant(
            id=input.id(),
            comments=input.comments(),
        )

        path = os.path.join(
            main_path, temp_path, input.date_selector(), input.people_selector()[0]
        )

        store_participant_metadata(path=path, metadata=person)

        if input.id() == "":
            ui.notification_show(
                f"You need to enter a valid ID before you can edit the session!",
                duration=None,
                type="warning",
            )
        elif input.people_selector()[0] != input.id():
            os.rename(
                path,
                os.path.join(main_path, temp_path, input.date_selector(), input.id()),
            )
            reset_user()

            ui.notification_show(
                f"Metadata has been edited and saved.",
                duration=None,
                type="default",
            )
            save_view_state.set(False)

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
    @reactive.event(input.save_yes)
    async def store_metadata():
        i = 0
        day = datetime.datetime.now().strftime(date_format)

        person = Participant(id=input.id(), comments=input.comments())

        amount_of_files = len(get_files_to_move())
        if input.rb_unsaved_days.is_set():
            day = input.rb_unsaved_days()

        with ui.Progress(min=1, max=amount_of_files) as p:
            p.set(message="Moving files in progress", detail="This may take a while...")

            for _ in move_data_from_temp_to_main_storage(
                folder_name=input.id(), participant=person, day=day
            ):
                i += 1
                p.set(i, message="Moving files")
                await asyncio.sleep(0.1)

        update_ui()
        reset_user()

    @reactive.Effect
    @reactive.event(input.reset_button)
    def reset_metadata():
        reset_user()

    def reset_user():
        ui.update_text("id", value="")
        ui.update_text("comments", value="")
