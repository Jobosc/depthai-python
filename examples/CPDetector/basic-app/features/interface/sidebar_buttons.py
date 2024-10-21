from shiny import render, ui

from features.functions import get_files_to_move
from features.reactivity.reactive_values import (
    unsaved_days,
    save_view_state,
)


def editor():
    @render.ui
    def forgotten_session_days():
        if unsaved_days.get():
            return [
                ui.input_radio_buttons(
                    "rb_unsaved_days",
                    "There are unsaved local sessions that need to be deleted or stored first:",
                    unsaved_days.get(),
                ),
                ui.input_action_button(
                    "delete_date_sessions",
                    "Delete old Sessions",
                    class_="btn-outline-danger",
                ),
            ]

    @render.ui
    def save_button_choice():
        if not save_view_state.get():
            return ui.input_task_button(
                "save_button", "Save", label_busy="Saving Session..."
            )
        else:
            return ui.input_action_button(
                "edit_metadata_button",
                "Save changes",
                label_busy="Saving Session...",
                class_="btn-warning",
            )

    @render.ui
    def delete_current_session_button_choice():
        number_of_files = get_files_to_move()
        if save_view_state.get():
            return ui.input_action_button(
                "cancel_edit_metadata_button",
                "Cancel",
                label_busy="Saving Session...",
                class_="btn-outline-secondary",
            )
        elif not unsaved_days.get() and number_of_files:
            return ui.input_task_button(
                "delete_current_session_button",
                "Delete current session",
                label_busy="Deleting Sessions...",
                class_="btn-outline-danger"
            )
        else:
            return None
