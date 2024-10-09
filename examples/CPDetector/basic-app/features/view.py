import faicons as fa
from shiny import ui

from features.functions import get_hard_drive_space

ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "calendar": fa.icon_svg("calendar"),
    "gear": fa.icon_svg("gear"),
    "film": fa.icon_svg("film"),
    "person-walking": fa.icon_svg("person-walking"),
}


def side_view():
    return (
        (
            ui.h4("Input data"),
            ui.input_dark_mode(),
            ui.input_text("id", "Enter ID"),
            ui.input_text_area("comments", ui.markdown("Comments"), autoresize=True),
            ui.panel_conditional(
                "input.id",
                ui.input_action_button(
                    "reset_button", "Reset", class_="btn-outline-danger"
                ),
            ),
            ui.output_ui("forgotten_session_days"),
            ui.output_ui("save_button_choice"),
            ui.panel_conditional(
                "input.id",
                ui.value_box(
                    ui.p(""),
                    ui.p("Patient"),
                    ui.output_ui("metadata_output"),
                    showcase=ICONS["user"],
                ),
            ),
            ui.tags.style(
                """
                    html, body {
                        height: 100%;
                        margin: 0;
                    }
                    .right-aligned {
                        text-align: right;
                        margin: 0;
                    }
                    .bottom-aligned-container {
                        position: absolute;
                        bottom: 0;
                        text-align: left;
                    }
                """
            ),
            ui.div(
                ui.layout_columns(
                    ui.p("View", class_="right-aligned"),
                    ui.input_switch("switch_mode", "Record", False),
                    fill=False,
                    fillable=True,
                    col_widths={"xs": (1, 1)},
                    gap="1em",
                ),
                class_="bottom-aligned-container",
            ),
        ),
    )


def header():
    total, used, free = get_hard_drive_space()
    divisor = 10 ** 9

    return ui.layout_columns(
        ui.panel_title("Videos"),
        ui.markdown(f"**Hard Drive:**"),
        ui.markdown(
            f"{total / divisor:.2f}GB - Used: {used / divisor:.2f}GB - Free: {free / divisor:.2f}GB"
        ),
        ui.output_ui("camera_led_update"),
        ui.markdown("Camera availability"),
        fill=False,
        fillable=True,
        col_widths={"xs": (5, 1, 3, 1, 2)},
        gap="0em",
    )


def main_view():
    return (
        ui.output_ui("header"),
        __cards(),
        __session_buttons(),
        ui.output_code("action"),
        ui.output_ui("display_recorded_session_title"),
        ui.layout_columns(
            ui.output_ui("update_date_selector"),
            ui.output_ui("update_people_selector"),
        ),
        ui.layout_columns(
            ui.output_ui("display_buttons"),
        ),
    )


def __dashboard(size: int, title: str, value: list, icon_name: str):
    return ui.column(
        size,
        ui.value_box(
            ui.p(title),
            *value,
            showcase=ICONS[icon_name],
        ),
    )


def __cards():
    block_size = 12
    return (
        ui.layout_columns(
            __dashboard(
                block_size,
                "Recorded users",
                [
                    ui.output_text("recorded_user"),
                    ui.output_text("recorded_user_today"),
                ],
                "person-walking",
            ),
            __dashboard(
                block_size,
                "Recorded sessions",
                [ui.output_text("recorded_session"), ui.output_text("recorded_days")],
                "film",
            ),
            __dashboard(
                block_size,
                "Date",
                [ui.output_text("current_time"), ui.output_text("current_day")],
                "calendar",
            ),
        ),
    )


def __session_buttons():
    return (
        ui.layout_columns(
            ui.input_action_button(
                "record_button",
                "Activate recording",
                # label_busy="Ready...",
                class_="btn-outline-success",
                # icon="▶️",
            ),
            ui.input_action_button(
                "show_sessions", "Display sessions", class_="btn-secondary"
            ),
        ),
    )
