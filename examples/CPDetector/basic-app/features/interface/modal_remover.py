"""
This module handles the modal operations for the application.

Classes:
    Modal: Manages the modal operations including saving, conversion, and deletion.
"""

from shiny import reactive, ui


class ModalRemover:
    """
    Manages the modal operations including saving, conversion, and deletion.

    Args:
        input: The input object for the server.
    """
    input = None

    def __init__(self, input):
        self.input = input
        self.saving_modal()
        self.conversion_modal()
        self.delete_modal()
        self.delete_current_session_modal()

    def saving_modal(self):
        """
        Handles the saving modal.

        Removes the modal when the save confirmation buttons are clicked.
        """

        @reactive.Effect
        @reactive.event(self.input.save_yes, self.input.save_no)
        def _():
            ui.modal_remove()

    def conversion_modal(self):
        """
        Handles the conversion modal.

        Removes the modal when the conversion confirmation buttons are clicked.
        """

        @reactive.Effect
        @reactive.event(self.input.convert_yes, self.input.convert_no)
        def _():
            ui.modal_remove()

    def delete_modal(self):
        """
        Handles the delete modal.

        Removes the modal when the delete confirmation buttons are clicked.
        """

        @reactive.Effect
        @reactive.event(self.input.delete_session_yes, self.input.delete_session_no)
        def _():
            ui.modal_remove()

    def delete_current_session_modal(self):
        """
        Handles the delete current session modal.

        Removes the modal when the delete current session confirmation buttons are clicked.
        """

        @reactive.Effect
        @reactive.event(self.input.delete_current_session_yes, self.input.delete_current_session_no)
        def _():
            ui.modal_remove()
