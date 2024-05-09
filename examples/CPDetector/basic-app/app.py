from shiny import reactive
from shiny.express import input, render, ui

from participant import Participant
import faicons as fa
import datetime
from video_recording import run
import functions as funcs
import asyncio


ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "calendar": fa.icon_svg("calendar"),
    "gear": fa.icon_svg("gear"),
    "film": fa.icon_svg("film"),
    "person-walking": fa.icon_svg("person-walking"),
}

users_all = reactive.value(funcs.get_amount_of_people_recorded_in_total())
users_today = reactive.value(f"Today: {funcs.get_amount_of_people_recorded_today()}")
sessions_all = reactive.value(funcs.get_amount_of_sessions_recorded_in_total())
days_all = reactive.value(f"Days recorded: {funcs.get_amount_of_days_recorded()}")


ui.page_opts(title="Gait Recording", fillable=True)
#######################################################
#                     Sidebar
#######################################################

with ui.sidebar(id="sidebar"):
    "Input data"

    ui.input_dark_mode(id="mode")

    # Input fields
    for attrs in vars(Participant()):
        ui.input_text(attrs, label=f"Enter {attrs}")

    ui.input_text_area(
        "comments",
        ui.markdown("Comments"),
        autoresize=True,
    )

    # Action Button
    ui.input_action_button("save_button", "Save")

    with ui.panel_conditional(
        "input.name || input.subjects || input.grade || input.gender"
    ):
        ui.input_action_button("reset_button", "Reset")

        with ui.value_box(showcase=ICONS["user"]):
            """"""
            "Metadata"

            @render.express
            def metadata_output():
                result = ""
                if input.name() != "":
                    result = result + f"Name: {input.name()}" + "\n"
                if input.subjects() != "":
                    result = result + f"Subjects: {input.subjects()} \n"
                if input.grade() != "":
                    result = result + f"Grade: {input.grade()}\n"
                if input.gender() != "":
                    result = result + f"Gender: {input.gender()}"
                result


#######################################################
#                   Main View
#######################################################

ui.panel_title("Videos")

with ui.layout_columns(fill=False):

    with ui.value_box(showcase=ICONS["person-walking"]):
        "Recorded users"

        @render.express
        def recorded_user():
            str(users_all.get())

        @render.express
        def recorded_user_today():
            str(users_today.get())

    with ui.value_box(showcase=ICONS["film"]):
        "Recorded sessions"

        @render.express
        def recorded_session():
            str(sessions_all.get())

        @render.express
        def recorded_days():
            str(days_all.get())

    with ui.value_box(showcase=ICONS["calendar"]):
        "Date"
        date = datetime.datetime.now().strftime("%d-%m-%Y")
        date


ui.input_slider("n", "N", 0, 100, 20)


# Action Button
ui.input_action_button("record_button", "Start recording")
"Press 'q' to stop recording."


"- (Show Time while running)"
"- (Show table of sessions recorded per participant)"
"- (Check if it is possible to show 'Stop recording' button)"
"- (Add possibility of deleting sessions and people from recorded data)"
"- (Add debug mode on second page, for settings)"
"- (Add switch to switch between normal video and depth camera)"
"- (Save metadata into a JSON or similar)"
# with ui.card():
#    ui.markdown(result)


def my_slider(id):
    return ui.input_slider(id, "N", 0, 100, 20)


#######################################################
#                    Events
#######################################################


@render.text
@reactive.event(input.save_button)
def store_metadata():
    test = Participant(
        name=input.name(),
        subjects=input.subjects(),
        grade=input.grade(),
        gender=input.gender(),
    )
    funcs.move_data_from_temp_to_main_storage(folder_name=input.name())

    # Update UI
    users_all.set(funcs.get_amount_of_people_recorded_in_total())
    users_today.set(f"Today: {funcs.get_amount_of_people_recorded_today()}")
    sessions_all.set(funcs.get_amount_of_sessions_recorded_in_total())
    days_all.set(f"Days recorded: {funcs.get_amount_of_days_recorded()}")

    reset_user()


@reactive.effect
@reactive.event(input.reset_button)
def reset_metadata():
    reset_user()


@reactive.effect
@reactive.event(input.record_button)
async def start_recording():
    run()


#######################################################
#                    Functions
#######################################################


def reset_user():
    ui.update_text("name", value=f"")
    ui.update_text("subjects", value=f"")
    ui.update_text("grade", value=f"")
    ui.update_text("gender", value=f"")
    ui.update_text("comments", value=f"")
