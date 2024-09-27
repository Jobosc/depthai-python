from shiny import render, reactive, ui

from features.functions import (
    create_date_selection_for_saved_sessions,
    get_recorded_people_for_a_specific_day,
)
from features.reactivity.reactive_values import session_view_state


def editor(input, output):
    @output
    @render.ui
    @reactive.event(input.show_sessions)
    def display_recorded_session_title():
        if input.unsaved_days.is_set():
            ui.notification_show(
                f"You need to complete the session from a previous day before you can start editing sessions!",
                duration=None,
                type="warning",
            )
        if not session_view_state.get():
            return ui.markdown("##### Recorded Sessions")

    @output
    @render.ui
    @reactive.event(input.show_sessions)
    def update_date_selector():
        if not input.unsaved_days.is_set():
            if session_view_state.get():
                session_view_state.set(False)
                ui.update_action_button("show_sessions", label="Display sessions")
                return None
            else:
                session_view_state.set(True)
                ui.update_action_button("show_sessions", label="Hide sessions")
                dates = {"": "Select..."}
                dates.update(create_date_selection_for_saved_sessions())

                return [
                    ui.br(),
                    ui.input_select(
                        "date_selector", "Choose a Date:", dates, width="100%"
                    ),
                ]

    @output
    @render.ui
    @reactive.event(input.date_selector, input.show_sessions)
    def update_people_selector():
        if not input.rb_unsaved_days.is_set() and session_view_state.get():
            if input.date_selector.get() != "":
                return [
                    ui.br(),
                    ui.input_selectize(
                        "people_selector",
                        "Choose Datasets:",
                        get_recorded_people_for_a_specific_day(
                            input.date_selector.get()
                        ),
                        multiple=True,
                        width="100%",
                    ),
                ]

    @output
    @render.ui
    @reactive.event(input.people_selector, input.show_sessions)
    def display_buttons():
        buttons = []
        datasets = input.people_selector.get()
        if datasets and session_view_state.get():
            buttons.append(
                ui.input_action_button(
                    "delete_dataset",
                    "Delete",
                    class_="btn-outline-danger",
                    width="100%",
                )
            )
            if len(datasets) == 1:  # Only show Edit button if only one is selected
                buttons.append(
                    ui.input_action_button(
                        "edit_dataset",
                        "Edit",
                        class_="btn-outline-secondary",
                        width="100%",
                    )
                )
        return buttons
