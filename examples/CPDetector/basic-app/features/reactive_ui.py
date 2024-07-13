import faicons as fa
from shiny import render, ui, reactive

from .functions import get_connection_states
from .reactive_values import unsaved_days, save_view_state

STATUS = {
    "available": fa.icon_svg(name="circle", fill="green"),
    "missing": fa.icon_svg(name="circle", fill="red"),
}


def values(output):
    @output
    @render.ui
    def forgotten_session_days():
        if unsaved_days.get():
            return [
                ui.input_radio_buttons(
                    "rb_unsaved_days",
                    "There are unsaved local sessions that need to be stored first:",
                    unsaved_days.get(),
                ),
                ui.input_action_button("delete_date_sessions", "Delete Sessions", class_="btn-outline-danger"),
            ]

    @output
    @render.ui
    def save_button_choice():
        if not save_view_state.get():
            return ui.input_task_button("save_button", "Save", label_busy="Saving Session...")
        else:
            return ui.input_action_button("edit_metadata_button", "Save changes", label_busy="Saving Session...",
                                          class_="btn-warning")

    @output
    @render.ui
    def connection():
        reactive.invalidate_later(1)
        connections = get_connection_states()
        return ui.layout_columns(
            ui.panel_title("Videos"),
            STATUS["available"] if connections[0] else STATUS["missing"],
            ui.markdown("Hard Drive connection"),
            STATUS["available"] if connections[1] else STATUS["missing"],
            ui.markdown("Camera connection"), fill=False, fillable=True, col_widths={"xs": (8, 1, 1, 1, 1)}, gap="0em",
        )
