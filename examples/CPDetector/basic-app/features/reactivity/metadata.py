import asyncio
import datetime
import os

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
from features.reactivity.reactive_updates import update_ui
from features.reactivity.reactive_values import save_view_state


def editor(input):
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
            __reset_user()

            ui.notification_show(
                f"Metadata has been edited and saved.",
                duration=None,
                type="default",
            )
            save_view_state.set(False)

    @reactive.Effect
    @reactive.event(input.save_yes)
    async def store_metadata():
        i = 0
        day = datetime.datetime.now().strftime(date_format)

        person = Participant(id=input.id(), comments=input.comments())

        amount_of_files = len(get_files_to_move())
        if input.rb_unsaved_days.is_set():
            day = input.rb_unsaved_days()

        if person.id == "":
            ui.notification_show(
                f"You need to enter a valid ID before you can store the session!",
                duration=None,
                type="warning",
            )
        
        elif amount_of_files == 0:
            ui.notification_show(
                f"No video recordings are available yet!",
                duration=None,
                type="warning",
            )

        else:
            with ui.Progress(min=1, max=amount_of_files) as p:
                p.set(
                    message="Moving files in progress",
                    detail="This may take a while...",
                )

                for _ in move_data_from_temp_to_main_storage(
                        folder_name=input.id(), participant=person, day=day
                ):
                    i += 1
                    p.set(i, message="Moving files")
                    await asyncio.sleep(0.1)

            update_ui()
            __reset_user()

    @reactive.Effect
    @reactive.event(input.reset_button, input.cancel_edit_metadata_button)
    def reset_metadata():
        __reset_user()

    def __reset_user():
        ui.update_text("id", value="")
        ui.update_text("comments", value="")
