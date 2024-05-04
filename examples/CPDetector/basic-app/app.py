from shiny import reactive
from shiny.express import input, render, ui

from participant import Participant


#######################################################
#                     Sidebar
#######################################################

with ui.sidebar(id="sidebar"):
    "Metadata"

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
    ui.input_action_button("reset_button", "Reset (?)")

    # Metadata to save
    @render.text(False)
    def text_out():
        result = ""
        if input.name() != "":
            result = result + f"Name: {input.name()}" + "\n"
        if input.subjects() != "":
            result = result + f"Subjects: {input.subjects()} \n"
        if input.grade() != "":
            result = result + f"Grade: {input.grade()}\n"
        if input.gender() != "":
            result = result + f"Gender: {input.gender()}"

        return result


#######################################################
#                     Main View
#######################################################

ui.panel_title("Gait Recorder")

metadata = reactive.value("0")


ui.input_slider("n", "N", 0, 100, 20)


def my_slider(id):
    return ui.input_slider(id, "N", 0, 100, 20)


# with ui.card():
#    ui.markdown(result)


#######################################################
#                     Events
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
    return f"{input.save_button()}"


@render.text
@reactive.event(input.reset_button)
def reset_metadata():
    pass  # input.name = ""


# @reactive.event(input.name)
@render.text
def name_metadata():
    if isinstance(input.name(), str):
        # result = result + f"**Name**: {input.name()}"
        pass  # metadata.set(input.name())
