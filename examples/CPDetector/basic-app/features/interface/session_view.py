import logging

from shiny import render, reactive, ui

from features.file_operations.read import list_people_for_a_specific_day, list_sessions_for_a_specific_person, \
    create_date_selection_for_saved_sessions
from features.modules.ui_state import UIState

ui_state = UIState()


def editor(input):
    session_view_state = reactive.Value(False)
    recording_view_state = reactive.Value(False)

    @render.ui
    @reactive.event(input.show_sessions)
    def display_recorded_session_title():  # Title: Recorded Sessions
        if ui_state.unsaved_days:
            session_view_state.set(False)
            recording_view_state.set(False)
            logging.warning("Sessions can't be displayed due to unsaved recordings.")
            ui.notification_show(
                f"You need to complete a previous session before you can start editing sessions!",
                duration=None,
                type="warning",
            )
        if not session_view_state.get() and not ui_state.unsaved_days:
            return ui.markdown("##### Recorded Sessions")

    @render.ui
    @reactive.event(input.show_sessions)
    def update_date_selector():  # Selector: Date Selector
        if not ui_state.unsaved_days:
            if session_view_state.get():
                logging.debug("Render UI: Remove date selector")
                session_view_state.set(False)
                recording_view_state.set(False)
                ui.update_action_button("show_sessions", label="Display sessions")
                ui_state.update_ui()
                return None
            else:
                logging.debug("Render UI: Display date selector")
                session_view_state.set(True)
                ui.update_action_button("show_sessions", label="Hide sessions")
                dates = {"": "Select..."}
                dates.update(create_date_selection_for_saved_sessions())
                ui_state.update_ui()
                return [
                    ui.input_select(
                        "date_selector", "Choose a Date:", dates, width="100%"
                    ),
                ]

    @render.ui
    @reactive.event(input.date_selector)
    def update_people_selector():  # Selector: People Selector
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
    @reactive.event(input.people_selector)
    def display_buttons():  # Buttons: Convert, Delete, Edit, Display Session
        buttons = []
        datasets = input.people_selector.get()
        if datasets and session_view_state.get():
            logging.debug("Render UI: Display Convert and Delete button.")
            buttons.append(
                ui.row(
                    ui.column(
                        12,  # Column width (out of 12) to adjust how much space each button takes
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
                            4,  # Column width (out of 12) to adjust how much space each button takes
                            ui.input_task_button(
                                "convert_dataset",
                                "Convert Recording(s)",
                                class_="btn-outline-warning",
                                label_busy="Conversion running...",
                                width="100%",
                            )
                        ),
                        ui.column(
                            4,  
                            ui.input_action_button(
                                "play_recording",
                                "Display Recording",
                                class_="btn-outline-info",
                                width="100%",
                            )
                        ),
                        ui.column(
                            4,
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
    def show_video_radio_buttons():  # Selector: Recordings Selector
        if session_view_state.get():
            if recording_view_state.get():
                recording_view_state.set(False)
                ui.update_action_button("play_recording", label="Display Recording")
                logging.debug("Render UI: Remove recordings selector.")
                return None
            elif input.date_selector.get() and input.people_selector.get():
                recording_view_state.set(True)
                ui.update_action_button("play_recording", label="Hide Recording")
                logging.debug("Render UI: Display recordings selector.")
                return ui.input_select(
                    "select_recordings",
                    "Select one of the recordings in this session:",
                    list_sessions_for_a_specific_person(day=input.date_selector.get(),
                                                        person_name=input.people_selector.get()[0]),
                    width="100%"
                ),
        return None

    @render.ui
    @reactive.event(input.select_recordings, recording_view_state)
    def display_recording():  # Video: Display Recording
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
