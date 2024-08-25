import datetime

from shiny import render, reactive, ui

from .functions import (
    create_date_selection_for_saved_sessions,
    get_recorded_people_for_a_specific_day,
    date_format,
    read_participant_metadata,
    delete_person_on_day_folder,
    delete_session_on_date_folder,
)
from .modules.participant import Participant
from .reactive_updates import update_ui
from .reactive_values import session_view_state, save_view_state
from .modules.camera import Camera


def values(input, output, camera: Camera):
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

    @reactive.Effect
    @reactive.event(input.delete_date_sessions)
    def initiate_session_deletion():
        day = ""
        if input.rb_unsaved_days.is_set():
            date = datetime.datetime.strptime(
                input.rb_unsaved_days(), date_format
            ).strftime("%Y-%m-%d")
            day = f", from {date}"
        notification = ui.modal(
            ui.markdown(
                f"**Do you really want to delete the recorded sessions{day}?**"
            ),
            ui.input_action_button("delete_yes", "Yes", class_="btn-danger"),
            ui.input_action_button("delete_no", "No", class_="btn-secondary"),
            easy_close=False,
            footer=None,
        )
        ui.modal_show(notification)

    @reactive.Effect
    @reactive.event(input.edit_dataset)
    def edit_metadata_dataset():
        metadata = read_participant_metadata(
            date=input.date_selector(), person=input.people_selector()[0]
        )
        person = Participant(**metadata)

        print(f"Editing metadata for {person.id}.")

        ui.update_text("id", value=person.id)
        ui.update_text("comments", value=person.comments)
        ui.update_radio_buttons("rb_unsaved_days", selected=None)

        save_view_state.set(True)

    @reactive.Effect
    @reactive.event(input.delete_dataset)
    def delete_dataset():
        for person in input.people_selector.get():
            state = delete_person_on_day_folder(
                day=input.date_selector.get(), person=person
            )

            if state:
                ui.notification_show(
                    f"Dataset deletion of '{person}' was successful.",
                    duration=None,
                    type="message",
                )
            else:
                ui.notification_show(
                    f"Deleting the dataset of '{person}' failed!",
                    duration=None,
                    type="error",
                )
        update_ui()

    @reactive.Effect
    @reactive.event(input.delete_yes)
    def delete_session_for_specific_day():
        print(input.rb_unsaved_days())
        state = delete_session_on_date_folder(day=input.rb_unsaved_days())
        day = datetime.datetime.strptime(input.rb_unsaved_days(), date_format).strftime(
            "%Y-%m-%d"
        )
        if state:
            ui.notification_show(
                f"Dataset deletion from '{day}' was successful.",
                duration=None,
                type="default",
            )
            ui.update_radio_buttons("rb_unsaved_days")
        else:
            ui.notification_show(
                f"Deleting the dataset from '{day}', failed!",
                duration=None,
                type="error",
            )
        update_ui()

    @reactive.Effect
    @reactive.event(input.switch_mode)
    def change_pipeline_mode():
        camera.mode = input.switch_mode()
