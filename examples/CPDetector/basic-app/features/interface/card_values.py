"""
This module handles the card value operations for the application.

Classes:
    CardValues: Manages the card value operations including displaying recorded users, sessions, days, and current time and day.

Functions:
    None
"""

import datetime
import logging

from shiny import render, reactive

from features.modules.ui_state import UIState


class CardValues:
    """
    Manages the card value operations including displaying recorded users, sessions, days, and current time and day.
    """
    ui_state = UIState()

    def __init__(self):
        self.recorded_user()
        self.recorded_user_today()
        self.recorded_session()
        self.recorded_days()
        self.current_time()
        self.current_day()

    def recorded_user(self):
        """
        Displays the total number of recorded users.

        Returns:
            str: The total number of recorded users.
        """

        @render.text
        def recorded_user() -> str:
            logging.debug("Render text: Collect text field for: all users.")
            return str(self.ui_state.users_all)

    def recorded_user_today(self):
        """
        Displays the number of recorded users for today.

        Returns:
            str: The number of recorded users for today.
        """

        @render.text
        def recorded_user_today() -> str:
            logging.debug("Render text: Collect text field for: users today.")
            return str(self.ui_state.users_today)

    def recorded_session(self):
        """
        Displays the total number of recorded sessions.

        Returns:
            str: The total number of recorded sessions.
        """

        @render.text
        def recorded_session() -> str:
            logging.debug("Render text: Collect text field for: all sessions.")
            return str(self.ui_state.sessions_all)

    def recorded_days(self):
        """
        Displays the total number of recorded days.

        Returns:
            str: The total number of recorded days.
        """

        @render.text
        def recorded_days() -> str:
            logging.debug("Render text: Collect text field for: all recorded days.")
            return str(self.ui_state.days_all)

    def current_time(self):
        """
        Displays the current time.

        Returns:
            str: The current time in HH:MM:SS format.
        """

        @render.text
        def current_time() -> str:
            reactive.invalidate_later(1)
            return datetime.datetime.now().strftime("%H:%M:%S")

    def current_day(self):
        """
        Displays the current day.

        Returns:
            str: The current day in DD-MM-YYYY format.
        """

        @render.text
        def current_day() -> str:
            logging.debug("Render text: Collect text field for: current day.")
            return datetime.datetime.now().strftime("%d-%m-%Y")
