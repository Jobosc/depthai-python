import asyncio
import datetime
import logging
import os

from shiny import ui, reactive

from features.file_operations.move import list_files_to_move, move_data_from_temp_to_main_storage
from features.file_operations.read import check_if_folder_already_exists
from features.modules.participant import Participant, read_participant_metadata
from features.modules.timestamps import Timestamps
from features.reactivity.reactive_values import save_view_state
from utils.parser import ENVParser
from features.reactivity.reactive_updates import UIState

ui_state = UIState()


def editor(input, timestamps: Timestamps):
    @reactive.Effect
    @reactive.event(input.edit_metadata_button)
    def edit_metadata():
        env = ENVParser()
        old_person = read_participant_metadata(
            date=input.date_selector(), person=input.people_selector()[0]
        )

        person = Participant(
            id=input.id(),
            comments=input.comments(),
            timestamps=old_person.timestamps
        )

        path = os.path.join(
            env.main_path, env.temp_path, input.date_selector(), input.people_selector()[0]
        )

        person.store_participant_metadata(path=str(path))

        if input.id() == "":
            logging.info("Metadata couldn't be edited due to a missing ID.")
            ui.notification_show(
                f"You need to enter a valid ID before you can edit the session!",
                duration=None,
                type="warning",
            )
        else:
            os.rename(
                path,
                os.path.join(env.main_path, env.temp_path, input.date_selector(), input.id()),
            )
            __reset_user()

            ui.notification_show(
                f"Metadata has been edited and saved.",
                duration=None,
                type="default",
            )
            save_view_state.set(False)
            logging.info("Metadata has been edited and saved successfully.")

    @reactive.Effect
    @reactive.event(input.save_yes)
    async def store_metadata():
        env = ENVParser()
        i = 0
        day = datetime.datetime.now().strftime(env.date_format)
        person = Participant(id=input.id(), comments=input.comments(), timestamps=timestamps)

        amount_of_files = len(list_files_to_move())
        if input.rb_unsaved_days.is_set():
            day = input.rb_unsaved_days()

        if person.id == "":
            logging.info("Recordings couldn't be saved due to a missing ID.")
            ui.notification_show(
                f"You need to enter a valid ID before you can store the session!",
                duration=None,
                type="warning",
            )

        elif amount_of_files == 0:
            logging.info("Recordings couldn't be saved due to missing files.")
            ui.notification_show(
                f"No video recordings are available yet!",
                duration=None,
                type="warning",
            )

        elif check_if_folder_already_exists(folder_id=input.id(), day=day):
            logging.info("Recordings couldn't be saved due to an already existing ID for the current day.")
            ui.notification_show(
                f"ID already exists for the day!",
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
                        folder_id=input.id(), participant=person, day=day
                ):
                    i += 1
                    p.set(i, message="Moving files")
                    await asyncio.sleep(0.1)

            __reset_user()
            logging.info("Recordings have been saved.")
        ui_state.update_ui()

    @reactive.Effect
    @reactive.event(input.reset_button, input.cancel_edit_metadata_button)
    def reset_metadata():
        __reset_user()

    def __reset_user():
        logging.debug("Metadata has been reset in the view.")
        ui.update_text("id", value="")
        ui.update_text("comments", value="")
