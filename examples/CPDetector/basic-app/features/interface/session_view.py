from shiny import render, reactive, ui

from features.file_operations.read_storage import list_people_for_a_specific_day
from features.functions import (
    create_date_selection_for_saved_sessions,
    get_recordings_for_a_specific_session,
)
from features.reactivity.reactive_updates import update_ui
from features.reactivity.reactive_values import session_view_state, recording_view_state, unsaved_days
import logging


def editor(input):
    @render.ui
    @reactive.event(input.show_sessions)
    def display_recorded_session_title():
        if unsaved_days.get():
            logging.warning("Sessions can't be displayed due to unsaved recordings.")
            ui.notification_show(
                f"You need to complete a previous session before you can start editing sessions!",
                duration=None,
                type="warning",
            )
        if not session_view_state.get() and not unsaved_days.get():
            return ui.markdown("##### Recorded Sessions")

    @render.ui
    @reactive.event(input.show_sessions)
    def update_date_selector():
        if not unsaved_days.get():
            if session_view_state.get():
                logging.debug("Render UI: Remove date selector")
                session_view_state.set(False)
                recording_view_state.set(False)
                ui.update_action_button("show_sessions", label="Display sessions")
                update_ui()
                return None
            else:
                logging.debug("Render UI: Display date selector")
                session_view_state.set(True)
                ui.update_action_button("show_sessions", label="Hide sessions")
                dates = {"": "Select..."}
                dates.update(create_date_selection_for_saved_sessions())
                update_ui()
                return [
                    ui.input_select(
                        "date_selector", "Choose a Date:", dates, width="100%"
                    ),
                ]

    @render.ui
    @reactive.event(input.date_selector, input.show_sessions)
    def update_people_selector():
        if not input.rb_unsaved_days.is_set() and session_view_state.get():
            if input.date_selector.get() != "":
                logging.debug("Render UI: Display ID selector")
                return [
                    ui.input_selectize(
                        "people_selector",
                        "Choose Datasets:",
                        list_people_for_a_specific_day(
                            input.date_selector.get()
                        ),
                        multiple=True,
                        width="100%",
                    ),
                ]

    @render.ui
    @reactive.event(input.people_selector, input.show_sessions)
    def display_buttons():
        buttons = []
        datasets = input.people_selector.get()
        if datasets and session_view_state.get():
            logging.debug("Render UI: Display Convert and Delete button.")
            buttons.append(
                ui.row(
                    ui.column(
                        6,  # Column width (out of 12) to adjust how much space each button takes
                        ui.input_task_button(
                            "convert_dataset",
                            "Convert Recording(s)",
                            class_="btn-outline-warning",
                            label_busy="Conversion running...",
                            width="100%",
                        )
                    ),
                    ui.column(
                        6,
                        ui.input_action_button(
                            "delete_dataset",
                            "Delete Session(s)",
                            class_="btn-outline-danger",
                            width="100%",
                        )
                    )
                ),
            )

            if len(datasets) == 1:  # Only show Edit button if only one is selected
                logging.debug("Render UI: Display Edit and Display Session button.")
                buttons.append(
                    ui.row(
                        ui.column(
                            6,  # Column width (out of 12) to adjust how much space each button takes
                            ui.input_action_button(
                                "play_recording",
                                "Display Recording",
                                class_="btn-outline-info",
                                width="100%",
                            )
                        ),
                        ui.column(
                            6,
                            ui.input_action_button(
                                "edit_dataset",
                                "Edit Session",
                                class_="btn-outline-secondary",
                                width="100%",
                            )
                        )
                    ),
                )
        return buttons

    @render.ui
    @reactive.event(input.play_recording)
    def show_video_radio_buttons():
        if session_view_state.get():
            if recording_view_state.get():
                recording_view_state.set(False)
                ui.update_action_button("play_recording", label="Display Recording")
                logging.debug("Render UI: Remove recordings selector.")
                return None
            else:
                recording_view_state.set(True)
                ui.update_action_button("play_recording", label="Hide Recording")
                logging.debug("Render UI: Display recordings selector.")
                return ui.input_select(
                    "select_recordings",
                    "Select one of the recordings in this session:",
                    get_recordings_for_a_specific_session(required_day=input.date_selector.get(),
                                                          person_name=input.people_selector.get()[0]),
                    width="100%"
                ),
        return None

    @render.ui
    @reactive.event(input.select_recordings, input.show_sessions)
    def display_recording():
        if session_view_state.get() and recording_view_state.get() and input.select_recordings.get():
            logging.debug("Render UI: Display video field.")
            return [ui.tags.video(
                ui.tags.source(src=input.select_recordings.get(), type="video/mp4"),
                controls=True,
                width="800px",
                autoplay=False
            ), ]
        else:
            logging.debug("Render UI: Remove video field.")
            return None
