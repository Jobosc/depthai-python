from shiny import reactive
from shiny.express import input, render, ui

from participant import Participant
import faicons as fa
import datetime
from video_recording import run
import functions as funcs
import asyncio
from dotenv import load_dotenv

load_dotenv(
    "/home/pi/Desktop/luxonis/depthai-python/examples/CPDetector/basic-app/.env"
)

ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "calendar": fa.icon_svg("calendar"),
    "gear": fa.icon_svg("gear"),
    "film": fa.icon_svg("film"),
    "person-walking": fa.icon_svg("person-walking"),
}

users_all = reactive.value(len(funcs.get_recorded_people_in_total()))
users_today = reactive.value(f"Today: {len(funcs.get_recorded_people_today())}")
sessions_all = reactive.value(len(funcs.get_all_recorded_sessions_so_far()))
days_all = reactive.value(f"Days recorded: {len(funcs.get_recorded_days())}")
selection_dates = reactive.value(funcs.create_date_selection())
start_time = reactive.value(datetime.datetime.now())

# ui.page_opts(title="Gait Recording", fillable=True)
#######################################################
#                     Sidebar
#######################################################

with ui.sidebar(id="sidebar"):
    ui.p("Input data")
    ui.input_dark_mode(id="mode")

    # Input fields
    for attrs in vars(Participant()):
        ui.input_text(attrs, label=f"Enter {attrs}")

    ui.input_text_area("comments", ui.markdown("Comments"), autoresize=True)

    # Action Button
    ui.input_task_button("save_button", "Save", label_busy="Saving Session...")

    with ui.panel_conditional(
        "input.name || input.subjects || input.grade || input.gender"
    ):
        ui.input_action_button("reset_button", "Reset", class_="btn-outline-danger")

        with ui.value_box(showcase=ICONS["user"]):
            ui.p("")
            ui.p("Metadata")

            @render.express
            def metadata_output():
                if input.name() != "":
                    ui.markdown(f"Name: {input.name()}")
                if input.subjects() != "":
                    ui.markdown(f"Subjects: {input.subjects()}")
                if input.grade() != "":
                    ui.markdown(f"Grade: {input.grade()}")
                if input.gender() != "":
                    ui.markdown(f"Gender: {input.gender()}")


#######################################################
#                   Main View
#######################################################

ui.panel_title("Videos")

# Top Cards
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


# Action Button
with ui.layout_columns(fill=False):
    ui.input_task_button(
        "record_button",
        "Start recording",
        label_busy="Recording...",
        class_="btn-success",
    )

    ui.input_action_button("show_sessions", "Display sessions", class_="btn-secondary")
ui.p("Press 'q' to stop recording.")

# TODO: Check if it works
with ui.panel_conditional("input.name || input.subjects"):

    @render.text
    def time_recorder():
        reactive.invalidate_later(1)
        time_delta = datetime.datetime.now() - start_time.get()
        return time_delta


# Recorded Sessions
with ui.panel_conditional("input.name || input.subjects"):
    ui.markdown("#### Recorded Sessions")
    ui.br()

    ui.input_select("date", "Choose a Date:", [])

    @render.text
    def value():
        return "You choose: " + str(input.date())


with ui.panel_conditional("input.name || input.subjects"):

    def my_accordion(**kwargs):
        with ui.accordion(**kwargs):
            for letter in "ABCDE":
                with ui.accordion_panel(f"Section {letter}"):
                    f"Some narrative for section {letter}"

    my_accordion(multiple=False, id="acc_single")
    ui.br()


"- (Show Time while running)"
"- (Show table of sessions recorded per participant)"
"- (Check if it is possible to show 'Stop recording' button)"
"- (Add possibility of deleting sessions and people from recorded data)"
"- (Add debug mode on second page, for settings)"
"- (Add switch to switch between normal video and depth camera)"
"- (Prevent code from starting if external hard drive is not connected)"
"- (Only save document if all metadata is filled, without comments)"
"- (Display free storage of the hard drive)"


#######################################################
#                    Events
#######################################################


@render.text
@reactive.event(input.save_button)
async def store_metadata():
    i = 0

    person = Participant(
        name=input.name(),
        subjects=input.subjects(),
        grade=input.grade(),
        gender=input.gender(),
    )

    amount_of_files = len(funcs.get_files_to_move())

    with ui.Progress(min=1, max=amount_of_files) as p:
        p.set(message="Moving files in progress", detail="This may take a while...")

        for _ in funcs.move_data_from_temp_to_main_storage(
            folder_name=input.name(), participant=person
        ):
            i += 1
            p.set(i, message="Moving files")
            await asyncio.sleep(0.1)

    # Update UI
    users_all.set(len(funcs.get_recorded_people_in_total()))
    users_today.set(f"Today: {len(funcs.get_recorded_people_today())}")
    sessions_all.set(len(funcs.get_all_recorded_sessions_so_far()))
    days_all.set(f"Days recorded: {len(funcs.get_recorded_days())}")

    reset_user()

    return "Done computing!"


@reactive.effect
@reactive.event(input.reset_button)
def reset_metadata():
    reset_user()


@reactive.effect
@reactive.event(input.record_button)
def start_recording():
    start_time.set(datetime.datetime.now())
    run()


@reactive.effect
@reactive.event(input.show_sessions)
def handle_cancel():
    run.cancel()


#######################################################
#                    Functions
#######################################################


def reset_user():
    ui.update_text("name", value=f"")
    ui.update_text("subjects", value=f"")
    ui.update_text("grade", value=f"")
    ui.update_text("gender", value=f"")
    ui.update_text("comments", value=f"")


# def my_slider(id):
#    return ui.input_slider(id, "N", 0, 100, 20)
# ui.input_slider("n", "N", 0, 100, 20)

# with ui.card():
#    ui.markdown(result)
