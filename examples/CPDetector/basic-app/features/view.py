"""
This module provides the UI components for the application.

It defines the side view, header, and main view of the application UI, as well as helper functions to create UI elements.

Functions:
    side_view: Returns the side view UI components.
    header: Returns the header UI components.
    main_view: Returns the main view UI components.
    __dashboard: Creates a dashboard UI component.
    __cards: Creates the cards UI components.
    __session_buttons: Creates the session buttons UI components.

"""

import os
import shutil

import faicons as fa
from shiny import ui

from utils.parser import ENVParser

ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "calendar": fa.icon_svg("calendar"),
    "gear": fa.icon_svg("gear"),
    "film": fa.icon_svg("film"),
    "person-walking": fa.icon_svg("person-walking"),
}


def side_view() -> tuple:
    """
    Returns the side view UI components.

    Returns:
        tuple: A tuple containing the side view UI components.
    """
    return (
        (
            ui.h4("Input data"),
            ui.input_dark_mode(),
            ui.input_text("id", "Enter ID"),
            ui.input_text_area("comments", ui.markdown("Comments"), autoresize=True),
            ui.output_ui("forgotten_session_days"),
            ui.output_ui("save_button_choice"),
            ui.panel_conditional(
                "input.id == '' ",
                ui.output_ui("delete_current_session_button_choice")
            ),
            ui.output_ui("cancel_edit_metadata_button_choice"),
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


def header() -> ui.layout_columns:
    """
    Returns the header UI components.

    Returns:
        ui.layout_columns: The header UI components.
    """
    env = ENVParser()
    total, used, free = 0, 0, 0
    if os.path.exists(env.main_path):
        total, used, free = shutil.disk_usage(env.main_path)
    divisor = 10 ** 9

    return ui.layout_columns(
        ui.panel_title("Videos"),
        ui.markdown(f"**Hard Drive:**"),
        ui.markdown(
            f"{total / divisor:.2f}GB - Used: {used / divisor:.2f}GB - Free: {free / divisor:.2f}GB"
        ),
        ui.output_ui("recording_led_update"),
        ui.markdown("Recording active"),
        ui.output_ui("camera_led_update"),
        ui.markdown("Camera availability"),
        fill=False,
        fillable=True,
        col_widths={"xs": (2, 1, 3, 1, 2, 1, 2)},
        gap="0em",
    )


def main_view() -> tuple:
    """
    Returns the main view UI components.

    Returns:
        tuple: A tuple containing the main view UI components.
    """
    return (
        ui.output_ui("header"),
        __cards(),
        __session_buttons(),

        ui.panel_conditional(
            "input.show_sessions % 2 == 1",
            ui.output_ui("display_recorded_session_title"),
            ui.layout_columns(
                ui.output_ui("update_date_selector"),
                ui.output_ui("update_people_selector"),
            ),
            ui.layout_columns(
                ui.output_ui("display_buttons"),
            ),
            ui.panel_conditional(
                "input.people_selector != ''",
                ui.output_ui("show_video_radio_buttons"),
                ui.panel_conditional(
                    "input.select_recordings != ''",
                    ui.output_ui("display_recording"),
                ),
            ),
        ),
    )


def __dashboard(size: int, title: str, value: list, icon_name: str) -> ui.column:
    """
    Creates a dashboard UI component.

    Args:
        size (int): The size of the dashboard.
        title (str): The title of the dashboard.
        value (list): The values to display in the dashboard.
        icon_name (str): The name of the icon to display in the dashboard.

    Returns:
        ui.column: The dashboard UI component.
    """
    return ui.column(
        size,
        ui.value_box(
            ui.p(title),
            *value,
            showcase=ICONS[icon_name],
        ),
    )


def __cards() -> tuple:
    """
    Creates the cards UI components.

    Returns:
        tuple: A tuple containing the cards UI components.
    """
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


def __session_buttons() -> ui.layout_columns:
    """
    Creates the recording and session button UI components.

    Returns:
        ui.layout_columns: The session buttons UI components.
    """
    return (
        ui.layout_columns(
            ui.input_action_button(
                "record_button",
                "Activate recording",
                class_="btn-outline-success",
            ),
            ui.input_action_button(
                "show_sessions", "Display sessions", class_="btn-primary"
            ),
        ),
    )
