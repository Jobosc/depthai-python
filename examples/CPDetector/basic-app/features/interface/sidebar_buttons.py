import logging

from shiny import render, ui

from features.file_operations.move import list_files_to_move
from features.reactivity.reactive_values import (
    save_view_state,
)
from features.modules.ui_state import UIState

ui_state = UIState()

def editor():
    @render.ui
    def save_button_choice():
        if not save_view_state.get():
            logging.debug("Render UI: Display button to save recordings.")
            return ui.input_task_button(
                "save_button", "Save", label_busy="Saving Session..."
            )
        else:
            logging.debug("Render UI: Display button to save edited metadata.")
            return ui.input_action_button(
                "edit_metadata_button",
                "Save changes",
                label_busy="Saving Session...",
                class_="btn-warning",
            )

    @render.ui
    def delete_current_session_button_choice():
        number_of_files = list_files_to_move()
        if save_view_state.get():
            logging.debug("Render UI: Display button to cancel metadata editing.")
            return ui.input_action_button(
                "cancel_edit_metadata_button",
                "Cancel",
                label_busy="Saving Session...",
                class_="btn-outline-secondary",
            )
        elif ui_state.unsaved_days and number_of_files:
            logging.debug("Render UI: Display button to delete current session.")
            return ui.input_task_button(
                "delete_current_session_button",
                "Delete current session",
                label_busy="Deleting Sessions...",
                class_="btn-outline-danger"
            )
        else:
            return None
