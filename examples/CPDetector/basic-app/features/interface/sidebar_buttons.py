"""
This module handles the sidebar button operations for the application.

Classes:
    SidebarButtons: Manages the sidebar button operations including save, delete, and cancel buttons.
"""

import logging

from shiny import render, ui

from features.modules.ui_state import UIState


class SidebarButtons:
    """
    Manages the sidebar button operations including save, delete, and cancel buttons.
    """
    ui_state = UIState()

    def __init__(self):
        self.save_button_choice()
        self.delete_current_session_button_choice()
        self.cancel_edit_metadata_button_choice()

    def save_button_choice(self):
        """
        Displays the save button based on the view state.

        Returns:
            ui: The UI element for the save button.
        """
        @render.ui
        def save_button_choice():
            if not self.ui_state.save_view_state:
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

    def delete_current_session_button_choice(self):
        """
        Displays the delete current session button if there are unsaved days.

        Returns:
            ui: The UI element for the delete current session button.
        """
        @render.ui
        def delete_current_session_button_choice():
            if self.ui_state.unsaved_days:
                logging.debug("Render UI: Display button to delete current session.")
                return ui.input_task_button(
                    "delete_current_session_button",
                    "Delete current session",
                    label_busy="Deleting Sessions...",
                    class_="btn-outline-danger"
                )
            else:
                return None

    def cancel_edit_metadata_button_choice(self):
        """
        Displays the cancel edit metadata button if the save view state is active.

        Returns:
            ui: The UI element for the cancel edit metadata button.
        """
        @render.ui
        def cancel_edit_metadata_button_choice():
            if self.ui_state.save_view_state:
                logging.debug("Render UI: Display button to cancel metadata editing.")
                return ui.input_action_button(
                    "cancel_edit_metadata_button",
                    "Cancel",
                    label_busy="Saving Session...",
                    class_="btn-outline-secondary",
                )
            else:
                return None