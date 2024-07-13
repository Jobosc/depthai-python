import datetime

from shiny import render, reactive

from .reactive_values import users_all, users_today, sessions_all, days_all


def values(output):
    @output
    @render.text
    def recorded_user():
        return str(users_all.get())

    @output
    @render.text
    def recorded_user_today():
        return str(users_today.get())

    @output
    @render.text
    def recorded_session():
        return str(sessions_all.get())

    @output
    @render.text
    def recorded_days():
        return str(days_all.get())

    @output
    @render.text
    def current_time():
        reactive.invalidate_later(1)
        return datetime.datetime.now().strftime("%H:%M:%S")

    @output
    @render.text
    def current_day():
        return datetime.datetime.now().strftime("%d-%m-%Y")
