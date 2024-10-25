import datetime
import logging

from shiny import render, reactive

from features.modules.ui_state import UIState

ui_state = UIState()

def values():
    @render.text
    def recorded_user():
        logging.debug("Render text: Collect text field for: all users.")
        return str(ui_state.users_all)

    @render.text
    def recorded_user_today():
        logging.debug("Render text: Collect text field for: users today.")
        return str(ui_state.users_today)

    @render.text
    def recorded_session():
        logging.debug("Render text: Collect text field for: all sessions.")
        return str(ui_state.sessions_all)

    @render.text
    def recorded_days():
        logging.debug("Render text: Collect text field for: all recorded days.")
        return str(ui_state.days_all)

    @render.text
    def current_time():
        reactive.invalidate_later(1)
        return datetime.datetime.now().strftime("%H:%M:%S")

    @render.text
    def current_day():
        logging.debug("Render text: Collect text field for: current day.")
        return datetime.datetime.now().strftime("%d-%m-%Y")
