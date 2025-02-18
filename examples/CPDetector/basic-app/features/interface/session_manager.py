"""
This module handles the session view operations for the application.

Classes:
    SessionManager: Manages the session view operations including displaying recorded sessions, updating selectors, and displaying buttons and recordings.
"""

import logging

from shiny import render, reactive, ui

from features.file_operations.read import list_people_for_a_specific_day, list_sessions_for_a_specific_person, \
    create_date_selection_for_saved_sessions
from features.modules.ui_state import UIState


class SessionManager:
    """
    Manages the session view operations including displaying recorded sessions, updating selectors, and displaying buttons and recordings.

    Args:
        input: The input object for the server.
    """
    session_view_state = reactive.Value(False)
    recording_view_state = reactive.Value(False)
    ui_state = UIState()

    def __init__(self, input):
        self.input = input
        self.display_recorded_session_title()
        self.update_date_selector()
        self.update_people_selector()
        self.display_buttons()
        self.show_video_radio_buttons()
        self.display_recording()

    def display_recorded_session_title(self):
        """
        Displays the title for recorded sessions.

        Shows a warning notification if there are unsaved recordings.
        """

        @render.ui
        @reactive.event(self.input.show_sessions)
        def display_recorded_session_title():
            if self.ui_state.unsaved_days:
                self.session_view_state.set(False)
                self.recording_view_state.set(False)
                logging.warning("Sessions can't be displayed due to unsaved recordings.")
                ui.notification_show(
                    f"You need to complete a previous session before you can start editing sessions!",
                    duration=None,
                    type="warning",
                )
            if not self.session_view_state.get() and not self.ui_state.unsaved_days:
                return ui.markdown("##### Recorded Sessions")

    def update_date_selector(self):
        """
        Updates the date selector.

        Displays or removes the date selector based on the session view state.
        """

        @render.ui
        @reactive.event(self.input.show_sessions)
        def update_date_selector():
            if not self.ui_state.unsaved_days:
                if self.session_view_state.get():
                    logging.debug("Render UI: Remove date selector")
                    self.session_view_state.set(False)
                    self.recording_view_state.set(False)
                    ui.update_action_button("show_sessions", label="Display sessions")
                    self.ui_state.update_ui()
                    return None
                else:
                    logging.debug("Render UI: Display date selector")
                    self.session_view_state.set(True)
                    ui.update_action_button("show_sessions", label="Hide sessions")
                    dates = {"": "Select..."}
                    dates.update(create_date_selection_for_saved_sessions())
                    self.ui_state.update_ui()
                    return [
                        ui.input_select(
                            "date_selector", "Choose a Date:", dates, width="100%"
                        ),
                    ]

    def update_people_selector(self):
        """
        Updates the people selector.

        Displays the people selector based on the selected date.
        """

        @render.ui
        @reactive.event(self.input.date_selector)
        def update_people_selector():
            if not self.input.rb_unsaved_days.is_set() and self.session_view_state.get():
                if self.input.date_selector.get() != "":
                    logging.debug("Render UI: Display ID selector")
                    return [
                        ui.input_selectize(
                            "people_selector",
                            "Choose Datasets:",
                            list_people_for_a_specific_day(
                                self.input.date_selector.get()
                            ),
                            multiple=True,
                            width="100%",
                        ),
                    ]

    def display_buttons(self):
        """
        Displays the buttons for converting, deleting, editing, and displaying sessions.

        Shows different buttons based on the selected datasets.
        """

        @render.ui
        @reactive.event(self.input.people_selector)
        def display_buttons():
            buttons = []
            datasets = self.input.people_selector.get()
            if datasets and self.session_view_state.get():
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

    def show_video_radio_buttons(self):
        """
        Displays the radio buttons for selecting recordings.

        Shows or hides the recordings selector based on the session and recording view states.
        """

        @render.ui
        @reactive.event(self.input.play_recording)
        def show_video_radio_buttons():
            if self.session_view_state.get():
                if self.recording_view_state.get():
                    self.recording_view_state.set(False)
                    ui.update_action_button("play_recording", label="Display Recording")
                    logging.debug("Render UI: Remove recordings selector.")
                    return None
                elif self.input.date_selector.get() and self.input.people_selector.get():
                    self.recording_view_state.set(True)
                    ui.update_action_button("play_recording", label="Hide Recording")
                    logging.debug("Render UI: Display recordings selector.")
                    return ui.input_select(
                        "select_recordings",
                        "Select one of the recordings in this session:",
                        list_sessions_for_a_specific_person(day=self.input.date_selector.get(),
                                                            person_name=self.input.people_selector.get()[0]),
                        width="100%"
                    ),
            return None

    def display_recording(self):
        """
        Displays the selected recording.

        Shows the video field based on the selected recording.
        """

        @render.ui
        @reactive.event(self.input.select_recordings, self.recording_view_state)
        def display_recording():
            if self.session_view_state.get() and self.recording_view_state.get() and self.input.select_recordings.get():
                logging.debug("Render UI: Display video field.")
                return [ui.tags.video(
                    ui.tags.source(src=self.input.select_recordings.get(), type="video/mp4"),
                    controls=True,
                    width="800px",
                    autoplay=False,
                    preload=True,
                    disablepictureinpicture=True,
                ), ]
            else:
                logging.debug("Render UI: Remove video field.")
                return None
