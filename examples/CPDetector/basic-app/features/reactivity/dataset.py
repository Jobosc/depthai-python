import datetime

from shiny import ui, reactive

from features.functions import read_participant_metadata, delete_person_on_day_folder
from features.video_processing import convert_individual_videos
from features.modules.participant import Participant
from features.reactivity.reactive_updates import update_ui
from features.reactivity.reactive_values import save_view_state
from utils.parser import ENVParser

def editor(input):
    @reactive.Effect
    @reactive.event(input.delete_date_sessions)
    def initiate_session_deletion():
        env = ENVParser()
        day = ""
        if input.rb_unsaved_days.is_set():
            date = datetime.datetime.strptime(
                input.rb_unsaved_days(), env.date_format
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
        person = read_participant_metadata(
            date=input.date_selector(), person=input.people_selector()[0]
        )

        print(f"Editing metadata for {person.id}.")

        ui.update_text("id", value=person.id)
        ui.update_text("comments", value=person.comments)
        ui.update_radio_buttons("rb_unsaved_days", selected=None)

        save_view_state.set(True)

    @reactive.Effect
    @reactive.event(input.delete_session_yes)
    def delete_session_yes():
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
    @reactive.event(input.convert_yes)
    def convert_dataset():
        for person in input.people_selector.get():
            convert_individual_videos(day=input.date_selector.get(), person=person)
        update_ui()
