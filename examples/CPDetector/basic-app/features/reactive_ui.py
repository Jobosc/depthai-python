from shiny import render, ui

from .reactive_values import (
    unsaved_days,
    save_view_state,
)


def values():
    @render.ui
    def forgotten_session_days():
        if unsaved_days.get():
            return [
                ui.input_radio_buttons(
                    "rb_unsaved_days",
                    "There are unsaved local sessions that need to be stored first:",
                    unsaved_days.get(),
                ),
                ui.input_action_button(
                    "delete_date_sessions",
                    "Delete Sessions",
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
