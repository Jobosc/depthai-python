import datetime
from shiny import render, reactive

from .reactive_values import users_all, users_today, sessions_all, days_all


def values():
    @render.text
    def recorded_user():
        return str(users_all.get())

    @render.text
    def recorded_user_today():
        return str(users_today.get())

    @render.text
    def recorded_session():
        return str(sessions_all.get())

    @render.text
    def recorded_days():
        return str(days_all.get())

    @render.text
    def current_time():
        reactive.invalidate_later(1)
        return datetime.datetime.now().strftime("%H:%M:%S")

    @render.text
    def current_day():
        return datetime.datetime.now().strftime("%d-%m-%Y")

    @render.code
    def action():
        return "Press 'q' to stop recording."
