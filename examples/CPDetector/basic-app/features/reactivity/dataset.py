import asyncio
import logging

from shiny import ui, reactive

from features.file_operations.delete import delete_person_on_day_folder
from features.file_operations.read import list_people_for_a_specific_day
from features.file_operations.video_processing import convert_individual_videos
from features.modules.participant import read_participant_metadata
from features.modules.ui_state import UIState

ui_state = UIState()


def editor(input):
    @reactive.Effect
    @reactive.event(input.edit_dataset)
    def edit_metadata_dataset():
        person = read_participant_metadata(
            date=input.date_selector(), person=input.people_selector()[0]
        )

        ui.update_text("id", value=person.id)
        ui.update_text("comments", value=person.comments)
        ui.update_radio_buttons("rb_unsaved_days", selected=None)
        ui_state.save_view_state = True
        logging.info(f"Editing metadata for {person.id}.")

    @reactive.Effect
    @reactive.event(input.delete_session_yes)
    def delete_session_yes():
        for person in input.people_selector.get():
            state = delete_person_on_day_folder(
                day=input.date_selector.get(), person=person
            )
            ui.update_selectize(
                "people_selector",
                choices=list_people_for_a_specific_day(
                    input.date_selector.get()
                ),
                selected=[],
            )

            if state:
                logging.info(f"Dataset deletion of '{person}' was successful.")
                ui.notification_show(
                    f"Dataset deletion of '{person}' was successful.",
                    duration=None,
                    type="message",
                )
            else:
                logging.info(f"Deleting the dataset of '{person}' failed!")
                ui.notification_show(
                    f"Deleting the dataset of '{person}' failed!",
                    duration=None,
                    type="error",
                )
        ui_state.update_ui()

    @reactive.Effect
    @reactive.event(input.convert_yes)
    async def convert_dataset():
        amount_of_conversions = 0
        i = 0

        for person in input.people_selector.get():
            metadata = read_participant_metadata(input.date_selector.get(), person)
            amount_of_conversions += len(metadata.timestamps.time_windows) * 2

        for person in input.people_selector.get():
            with ui.Progress(min=1, max=amount_of_conversions) as p:
                p.set(i,
                      message="Converting videos in progress",
                      detail="This will take a while...",
                      )

                for _ in convert_individual_videos(day=input.date_selector.get(), person=person):
                    i += 1
                    p.set(i, message="Converting videos in progress", detail="This will take a while...", )
                    await asyncio.sleep(0.1)
        logging.info("Conversion of all files has been completed.")
        ui_state.update_ui()
