import datetime
import logging

from shiny import render, reactive

from features.reactivity.reactive_values import users_all, users_today, sessions_all, days_all


def values():
    @render.text
    def recorded_user():
        logging.debug("Render text: Collect text field for: all users.")
        return str(users_all.get())

    @render.text
    def recorded_user_today():
        logging.debug("Render text: Collect text field for: users today.")
        return str(users_today.get())

    @render.text
    def recorded_session():
        logging.debug("Render text: Collect text field for: all sessions.")
        return str(sessions_all.get())

    @render.text
    def recorded_days():
        logging.debug("Render text: Collect text field for: all recorded days.")
        return str(days_all.get())

    @render.text
    def current_time():
        reactive.invalidate_later(1)
        return datetime.datetime.now().strftime("%H:%M:%S")

    @render.text
    def current_day():
        logging.debug("Render text: Collect text field for: current day.")
        return datetime.datetime.now().strftime("%d-%m-%Y")
