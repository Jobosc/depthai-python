"""
This module handles the dataset operations such as editing metadata, deleting sessions, and converting datasets.

Classes:
    StorageController: Manages the dataset operations including editing metadata, deleting sessions, and converting datasets.
"""

import asyncio
import logging

from shiny import ui, reactive

from features.file_operations.delete import delete_person_on_day_folder
from features.file_operations.read import list_people_for_a_specific_day
from features.file_operations.video_processing import convert_individual_videos
from features.modules.participant import read_participant_metadata
from features.modules.ui_state import UIState


class StorageController:
    """
    Manages the dataset operations including editing metadata, deleting sessions, and converting datasets.

    Args:
        input: The input object for the server.
    """
    input = None
    ui_state = UIState()

    def __init__(self, input):
        self.input = input
        self.edit_metadata_dataset()
        self.delete_session_yes()
        self.convert_dataset()

    def edit_metadata_dataset(self):
        """
        Edits the metadata for the selected dataset.

        Reads the metadata for the selected person and updates the UI fields.
        """

        @reactive.Effect
        @reactive.event(self.input.edit_dataset)
        def _():
            person = read_participant_metadata(
                date=self.input.date_selector(), person=self.input.people_selector()[0]
            )

            ui.update_text("id", value=person.id)
            ui.update_text("comments", value=person.comments)
            ui.update_radio_buttons("rb_unsaved_days", selected=None)
            self.ui_state.save_view_state = True
            logging.info(f"Editing metadata for {person.id}.")

    def delete_session_yes(self):
        """
        Deletes the selected session.

        Deletes the dataset for the selected person on the selected day and updates the UI.
        """

        @reactive.Effect
        @reactive.event(self.input.delete_session_yes)
        def _():
            for person in self.input.people_selector.get():
                state = delete_person_on_day_folder(
                    day=self.input.date_selector.get(), person=person
                )
                ui.update_selectize(
                    "people_selector",
                    choices=list_people_for_a_specific_day(
                        self.input.date_selector.get()
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
            self.ui_state.update_ui()

    def convert_dataset(self):
        """
        Converts the dataset for the selected session.

        Converts the videos for the selected person on the selected day and updates the UI.
        """

        @reactive.Effect
        @reactive.event(self.input.convert_yes)
        async def _():
            amount_of_conversions = 0
            i = 0

            for person in self.input.people_selector.get():
                metadata = read_participant_metadata(self.input.date_selector.get(), person)
                amount_of_conversions += len(metadata.timestamps.time_windows) * 2

            for person in self.input.people_selector.get():
                with ui.Progress(min=1, max=amount_of_conversions) as p:
                    p.set(i,
                          message="Converting videos in progress",
                          detail="This will take a while...",
                          )

                    for _ in convert_individual_videos(day=self.input.date_selector.get(), person=person):
                        i += 1
                        p.set(i, message="Converting videos in progress", detail="This will take a while...", )
                        await asyncio.sleep(0.1)
            logging.info("Conversion of all files has been completed.")
            self.ui_state.update_ui()
