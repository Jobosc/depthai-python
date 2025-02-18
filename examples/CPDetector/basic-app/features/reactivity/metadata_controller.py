"""
This module handles the metadata editing and storing functionality for the application.

Classes:
    MetadataController: Sets up the reactive effects for editing, storing, and resetting metadata.
"""
import asyncio
import datetime
import logging
import os

from shiny import ui, reactive, render

from features.file_operations.move import list_files_to_move, move_data_from_temp_to_main_storage
from features.file_operations.read import check_if_folder_already_exists
from features.modules.participant import Participant, read_participant_metadata
from features.modules.ui_state import UIState
from utils.parser import ENVParser

ui_state = UIState()


class MetadataController:
    """
    Sets up the reactive effects for editing, storing, and resetting metadata.

    Args:
        input: The input object for the server.
    """
    input = None

    def __init__(self, input):
        self.input = input
        self.reset_metadata()
        self.edit_metadata()
        self.store_metadata()
        self.card()

    def card(self):
        """
        Renders the metadata output as a card.

        This method sets up a reactive UI element that displays the metadata, including the ID and comments, in a card format.

        Returns:
            list: A list of UI elements displaying the ID and comments.
        """

        @render.ui
        def metadata_output() -> list:
            elements = []
            if self.input.id() != "":
                elements.append(ui.markdown(f"ID: {self.input.id()}"))
            if self.input.comments() != "":
                elements.append(ui.br())
                elements.append(ui.markdown("Comments:"))
                elements.append(ui.markdown(f"{self.input.comments()}"))
            return elements

    def edit_metadata(self):
        """
        Edits the metadata for the current session.

        Reads the old metadata, updates it with the new values, and stores it.
        """

        @reactive.Effect
        @reactive.event(self.input.edit_metadata_button)
        def _():
            env = ENVParser()
            old_person = read_participant_metadata(
                date=self.input.date_selector(), person=self.input.people_selector()[0]
            )

            person = Participant(
                id=self.input.id(),
                comments=self.input.comments()
            )

            path = os.path.join(
                env.main_path, env.temp_path, self.input.date_selector(), self.input.people_selector()[0]
            )

            person.store_participant_metadata(path=str(path))

            if self.input.id() == "":
                logging.info("Metadata couldn't be edited due to a missing ID.")
                ui.notification_show(
                    f"You need to enter a valid ID before you can edit the session!",
                    duration=None,
                    type="warning",
                )
            else:
                os.rename(
                    path,
                    os.path.join(env.main_path, env.temp_path, self.input.date_selector(), self.input.id()),
                )
                self.__reset_user()

                ui.notification_show(
                    f"Metadata has been edited and saved.",
                    duration=None,
                    type="default",
                )
                ui_state.save_view_state = False
                logging.info("Metadata has been edited and saved successfully.")

    def store_metadata(self):
        """
        Stores the metadata for the current session.

        Moves the files from the temporary storage to the main storage and updates the UI.
        """

        @reactive.Effect
        @reactive.event(self.input.save_yes)
        async def _():
            print("Saving metadata")
            env = ENVParser()
            i = 0
            day = datetime.datetime.now().strftime(env.date_format)
            person = Participant(id=self.input.id(), comments=self.input.comments())

            amount_of_files = len(list_files_to_move())
            if self.input.rb_unsaved_days.is_set():
                day = self.input.rb_unsaved_days()

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

            elif check_if_folder_already_exists(folder_id=self.input.id(), day=day):
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
                            folder_id=self.input.id(), participant=person, day=day
                    ):
                        i += 1
                        p.set(i, message="Moving files")
                        await asyncio.sleep(0.1)

                self.__reset_user()
                logging.info("Recordings have been saved.")
            ui_state.update_ui()

    def reset_metadata(self):
        """
        Resets the metadata in the UI.

        Clears the input fields for ID and comments.
        """

        @reactive.Effect
        @reactive.event(self.input.cancel_edit_metadata_button)
        def _():
            self.__reset_user()

    def __reset_user(self):
        """
        Helper function to reset the user input fields.

        Clears the ID and comments fields and logs the reset action.
        """
        logging.debug("Metadata has been reset in the view.")
        ui.update_text("id", value="")
        ui.update_text("comments", value="")
