import asyncio
import datetime
import os

import faicons as fa
from dotenv import load_dotenv
from shiny import reactive
from shiny.express import input, render, ui

import functions as funcs
from participant import Participant
from video_recording import run

load_dotenv("./.env")

ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "calendar": fa.icon_svg("calendar"),
    "gear": fa.icon_svg("gear"),
    "film": fa.icon_svg("film"),
    "person-walking": fa.icon_svg("person-walking"),
}

STATUS = {
    "available": fa.icon_svg(name="circle", fill="green"),
    "missing": fa.icon_svg(name="circle", fill="red"),
}

temp_path = os.getenv("TEMP_STORAGE")
main_path = os.getenv("MAIN_STORAGE")
date_format = os.getenv("DATE_FORMAT")

# Variables to display stored data
users_all = reactive.value(len(funcs.get_recorded_people_in_total()))
users_today = reactive.value(
    f"Today: {len(funcs.get_recorded_people_for_a_specific_day())}"
)
sessions_all = reactive.value(len(funcs.get_all_recorded_sessions_so_far()))
days_all = reactive.value(f"Days recorded: {len(funcs.get_recorded_days())}")
unsaved_days = reactive.value(funcs.create_date_selection_for_unsaved_sessions())
#
session_view_state = reactive.value(False)
save_view_state = reactive.value(False)
start_time = reactive.value(datetime.datetime.now())

ui.page_opts(title="Gait Recording", fillable=True)
#######################################################
#                     Sidebar
#######################################################

with ui.sidebar(id="sidebar"):
    ui.p("Input data")
    ui.input_dark_mode(id="mode")

    # Input fields
    ui.input_text("id", label=f"Enter ID")

    ui.input_text_area("comments", ui.markdown("Comments"), autoresize=True)

    with ui.panel_conditional("input.id"):
        ui.input_action_button("reset_button", "Reset", class_="btn-outline-danger")

    @render.express
    def forgotten_session_days():
        if unsaved_days.get():
            ui.input_radio_buttons(
                "rb_unsaved_days",
                "There are unsaved local sessions that need to be stored first:",
                unsaved_days.get(),
            )
            ui.input_action_button(
                "delete_date_sessions", "Delete Sessions", class_="btn-outline-danger"
            ),

    # Action Button
    @render.express
    def save_button_choice():
        if not save_view_state.get():
            ui.input_task_button("save_button", "Save", label_busy="Saving Session...")
        else:
            ui.input_action_button(
                "edit_metadata_button",
                "Save changes",
                label_busy="Saving Session...",
                class_="btn-warning",
            )

    with ui.panel_conditional("input.id"):

        with ui.value_box(showcase=ICONS["user"]):
            ui.p("")
            ui.p("Patient")

            @render.express
            def metadata_output():
                if input.id() != "":
                    ui.markdown(f"ID: {input.id()}")
                if input.comments() != "":
                    ui.br()
                    ui.markdown("Comments:")
                    ui.markdown(f"{input.comments()}")


#######################################################
#                   Main View
#######################################################

with ui.layout_columns(fill=False):
    ui.panel_title("Videos")

# Top Cards section
with ui.layout_columns(fill=False):
    with ui.value_box(showcase=ICONS["person-walking"]):
        ui.p("Recorded users")

        @render.express
        def recorded_user():
            str(users_all.get())

        @render.express
        def recorded_user_today():
            str(users_today.get())

    with ui.value_box(showcase=ICONS["film"]):
        ui.p("Recorded sessions")

        @render.express
        def recorded_session():
            str(sessions_all.get())

        @render.express
        def recorded_days():
            str(days_all.get())

    with ui.value_box(showcase=ICONS["calendar"]):
        ui.p("Date")
        datetime.datetime.now().strftime("%d-%m-%Y")

        @render.text
        def current_time():
            reactive.invalidate_later(1)
            return datetime.datetime.now().strftime("%H:%M:%S")


# Action Buttons section
with ui.layout_columns(fill=False):
    # Start recording
    ui.input_task_button(
        "record_button",
        "Start recording",
        label_busy="Recording...",
        class_="btn-success",
        icon="▶️",
    )

    # Display sessions
    ui.input_action_button("show_sessions", "Display sessions", class_="btn-secondary")


@render.code
def action():
    return "Press 'q' to stop recording."


# Recorded Sessions section
@render.ui
@reactive.event(input.show_sessions)
def display_recorded_session_title():
    if input.rb_unsaved_days.is_set():
        ui.notification_show(
            f"You need to complete the session from a previous day before you can start editing sessions!",
            duration=None,
            type="warning",
        )
    if not session_view_state.get():
        return [ui.markdown("##### Recorded Sessions")]


with ui.layout_columns(fill=False):
    # Date Selector
    @render.ui
    @reactive.event(input.show_sessions)
    def update_date_selector():
        if not input.rb_unsaved_days.is_set():
            if session_view_state.get():
                session_view_state.set(False)
                ui.update_action_button("show_sessions", label="Display sessions")
                return None
            else:
                session_view_state.set(True)
                ui.update_action_button("show_sessions", label="Hide sessions")
                dates = {"": "Select..."}
                dates.update(funcs.create_date_selection_for_saved_sessions())
                return [
                    ui.br(),
                    ui.input_select(
                        "date_selector", "Choose a Date:", dates, width="100%"
                    ),
                ]

    # People Selector
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
                        funcs.get_recorded_people_for_a_specific_day(
                            input.date_selector.get()
                        ),
                        multiple=True,
                        width="100%",
                    ),
                ]


# Buttons for Dataset adaptation
@render.ui
@reactive.event(input.people_selector, input.show_sessions)
def display_buttons():
    buttons = []
    datasets = input.people_selector.get()
    if datasets and session_view_state.get():
        buttons.append(
            ui.input_action_button(
                "delete_dataset", "Delete", class_="btn-outline-danger", width="45%"
            ),
        )

        if len(datasets) == 1:  # Only show Edit button if only one is selected
            buttons.append(
                ui.input_action_button(
                    "edit_dataset", "Edit", class_="btn-outline-secondary", width="45%"
                )
            )

        return buttons


# "- (Check if it is possible to show 'Stop recording' button)"
# "- (Add debug mode on second page, for settings)"
# "- (Add switch to switch between normal video and depth camera)"
# "- (Prevent code from starting if external hard drive is not connected)"
# "- (Display free storage of the hard drive)"
# "- (Add status leds for connected connected camera and connected hard drive"
# Find out why video recording crashes after some time


#######################################################
#                    Events
#######################################################


# Modal button effects
@reactive.effect
@reactive.event(input.delete_date_sessions)
def initiate_session_deletion():
    day = ""
    if input.rb_unsaved_days.is_set():
        date = datetime.datetime.strptime(
            input.rb_unsaved_days(), date_format
        ).strftime("%Y-%m-%d")
        day = f", from {date}"

    notification = ui.modal(
        ui.markdown(f"**Do you really want to delete the recorded sessions{day}?**"),
        ui.input_action_button("delete_yes", "Yes", class_="btn-danger"),
        ui.input_action_button("delete_no", "No", class_="btn-secondary"),
        easy_close=False,
        footer=None,
    )
    ui.modal_show(notification)


@reactive.effect
@reactive.event(input.delete_yes, input.delete_no)
def modal_remover_delete():
    ui.modal_remove()


@reactive.effect
@reactive.event(input.save_button)
def initiate_save():
    day = ""
    if input.rb_unsaved_days.is_set():
        date = datetime.datetime.strptime(
            input.rb_unsaved_days(), date_format
        ).strftime("%Y-%m-%d")
        day = f", from {date}"

    notification = ui.modal(
        ui.markdown(f"**Do you really want to save the recorded sessions{day}?**"),
        ui.input_action_button("save_yes", "✔ Yes", class_="btn-success"),
        ui.input_action_button("save_no", "✘ No", class_="btn-danger"),
        easy_close=False,
        footer=None,
    )
    ui.modal_show(notification)


@reactive.effect
@reactive.event(input.save_yes, input.save_no)
def modal_remover():
    ui.modal_remove()


# Button effects
@render.text
@reactive.event(input.save_yes)
async def store_metadata():
    i = 0
    day = datetime.datetime.now().strftime(date_format)

    person = Participant(id=input.id(), comments=input.comments())

    amount_of_files = len(funcs.get_files_to_move())
    if input.rb_unsaved_days.is_set():
        day = input.rb_unsaved_days()

    with ui.Progress(min=1, max=amount_of_files) as p:
        p.set(message="Moving files in progress", detail="This may take a while...")

        for _ in funcs.move_data_from_temp_to_main_storage(
            folder_name=input.id(), participant=person, day=day
        ):
            i += 1
            p.set(i, message="Moving files")
            await asyncio.sleep(0.1)

    update_ui()
    reset_user()


@render.text
@reactive.event(input.delete_yes)
def delete_session_for_specific_day():
    state = funcs.delete_session_on_date_folder(day=input.rb_unsaved_days())
    day = datetime.datetime.strptime(input.rb_unsaved_days(), date_format).strftime(
        "%Y-%m-%d"
    )

    if state:
        ui.notification_show(
            f"Dataset deletion from '{day}' was successful.",
            duration=None,
            type="default",
        )
    else:
        ui.notification_show(
            f"Deleting the dataset from '{day}', failed!",
            duration=None,
            type="error",
        )
    print("Test")
    print(input.rb_unsaved_days())

    update_ui()


@reactive.effect
@reactive.event(input.reset_button)
def reset_metadata():
    reset_user()


@reactive.effect
@reactive.event(input.record_button)
def start_recording():
    if input.rb_unsaved_days.is_set():
        ui.notification_show(
            f"You need to complete the session from a previous day before you can start recording again!",
            duration=None,
            type="warning",
        )
    else:
        start_time.set(datetime.datetime.now())
        run()
        update_ui()


@reactive.effect
@reactive.event(input.delete_dataset)
def delete_dataset():
    for person in input.people_selector.get():
        state = funcs.delete_person_on_day_folder(
            day=input.date_selector.get(), person=person
        )

        if state:
            ui.notification_show(
                f"Dataset deletion of '{person}' was succesful.",
                duration=None,
                type="message",
            )
        else:
            ui.notification_show(
                f"Deleting the dataset of '{person}', failed!",
                duration=None,
                type="error",
            )

    update_ui()


@reactive.effect
@reactive.event(input.edit_dataset)
def edit_metadata():
    metadata = funcs.read_participant_metadata(
        date=input.date_selector(), person=input.people_selector()[0]
    )
    person = Participant(**metadata)

    ui.update_text("id", value=person.id)
    ui.update_text("comments", value=person.comments)
    ui.update_radio_buttons("rb_unsaved_days", selected=None)

    save_view_state.set(True)


@reactive.effect
@reactive.event(input.edit_metadata_button)
def edit_metadata():
    person = Participant(
        id=input.id(),
        comments=input.comments(),
    )

    path = os.path.join(
        main_path, temp_path, input.date_selector(), input.people_selector()[0]
    )

    funcs.store_participant_metadata(path=path, metadata=person)
    reset_user()

    ui.notification_show(
        f"Metadata has been edited and saved.",
        duration=None,
        type="default",
    )
    save_view_state.set(False)


#######################################################
#                    Functions
#######################################################


def reset_user():
    ui.update_text("id", value=f"")
    ui.update_text("comments", value=f"")


def update_ui():
    users_all.set(len(funcs.get_recorded_people_in_total()))
    users_today.set(f"Today: {len(funcs.get_recorded_people_for_a_specific_day())}")
    sessions_all.set(len(funcs.get_all_recorded_sessions_so_far()))
    days_all.set(f"Days recorded: {len(funcs.get_recorded_days())}")
    unsaved_days.set(funcs.create_date_selection_for_unsaved_sessions())


# def my_slider(id):
#    return ui.input_slider(id, "N", 0, 100, 20)
# ui.input_slider("n", "N", 0, 100, 20)

# with ui.card():
#    ui.markdown(result)
