import datetime
import asyncio

from shiny import ui, reactive

from features.file_operations.delete import delete_person_on_day_folder
from features.modules.participant import read_participant_metadata
from features.reactivity.reactive_updates import update_ui
from features.reactivity.reactive_values import save_view_state
from features.video_processing import convert_individual_videos
from utils.parser import ENVParser
import logging

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
        logging.info(f"Initiate deletion of session with a displayed modal.")

    @reactive.Effect
    @reactive.event(input.edit_dataset)
    def edit_metadata_dataset():
        person = read_participant_metadata(
            date=input.date_selector(), person=input.people_selector()[0]
        )

        ui.update_text("id", value=person.id)
        ui.update_text("comments", value=person.comments)
        ui.update_radio_buttons("rb_unsaved_days", selected=None)
        save_view_state.set(True)
        logging.info(f"Editing metadata for {person.id}.")
        
    @reactive.Effect
    @reactive.event(input.delete_session_yes)
    def delete_session_yes():
        for person in input.people_selector.get():
            state = delete_person_on_day_folder(
                day=input.date_selector.get(), person=person
            )

            if state:
                logging.info(f"Dataset deletion of '{person}' was successful.")
                ui.notification_show(
                    f"Dataset deletion of '{person}' was successful.",
                    duration=None,
                    type="message",
                )
            else:
                logging.info(f"Deleting the dataset of '{person}' failed!")
                ui.notification_show(
                    f"Deleting the dataset of '{person}' failed!",
                    duration=None,
                    type="error",
                )
        update_ui()

    @reactive.Effect
    @reactive.event(input.convert_dataset)
    async def convert_dataset():
        amount_of_conversions = 0
        i = 0

        for person in input.people_selector.get():
            metadata = read_participant_metadata(input.date_selector.get(), person)
            amount_of_conversions += len(metadata.timestamps.time_windows) * 2

        for person in input.people_selector.get():
            with ui.Progress(min=1, max=amount_of_conversions) as p:
                p.set(i,
                    message="Converting videos in progress",
                    detail="This will take a while...",
                )

                for _ in convert_individual_videos(day=input.date_selector.get(), person=person):
                    i += 1
                    p.set(i, message="Converting videos in progress", detail="This will take a while...",)
                    await asyncio.sleep(0.1)
        logging.info("Conversion of all files has been completed.")
        update_ui()
