"""
This module provides the UIState class for managing the UI state of the application.

Classes:
    UIState: Manages the UI state including users, sessions, days recorded, and unsaved days.

Methods:
    update_ui: Updates the UI state values.
    users_all: Returns the total number of users.
    users_today: Returns the number of users for today.
    sessions_all: Returns the total number of sessions.
    days_all: Returns the total number of days recorded.
    unsaved_days: Returns the unsaved days.
    save_view_state: Gets or sets the save view state.
"""

import logging

from shiny import reactive

from features.file_operations.read import list_days, list_people_for_a_specific_day, \
    list_people_in_total, list_sessions_in_total, create_date_selection_for_unsaved_sessions


class UIState:
    """
    Manages the UI state including users, sessions, days recorded, and unsaved days.

    Attributes:
        _instance (UIState): Singleton instance of the UIState class.
        __users_all (reactive.Value): Reactive value for the total number of users.
        __users_today (reactive.Value): Reactive value for the number of users for today.
        __sessions_all (reactive.Value): Reactive value for the total number of sessions.
        __days_all (reactive.Value): Reactive value for the total number of days recorded.
        __unsaved_days (reactive.Value): Reactive value for the unsaved days.
        __save_view_state (reactive.Value): Reactive value for the save view state.
    """
    _instance = None
    __users_all = reactive.Value(len(list_people_in_total()))
    __users_today = reactive.Value(f"Today: {len(list_people_for_a_specific_day())}")
    __sessions_all = reactive.Value(len(list_sessions_in_total()))
    __days_all = reactive.Value(f"Days recorded: {len(list_days())}")
    __unsaved_days = reactive.Value(create_date_selection_for_unsaved_sessions())
    __save_view_state = reactive.Value(False)

    def __new__(cls):
        if cls._instance is None:
            logging.debug("Initiate UIState instance.")
            cls._instance = super(UIState, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.update_ui()

    def update_ui(self) -> None:
        """
        Updates the UI state values.
        """
        self.__users_all.set(len(list_people_in_total()))
        self.__users_today.set(f"Today: {len(list_people_for_a_specific_day())}")
        self.__sessions_all.set(len(list_sessions_in_total()))
        self.__days_all.set(f"Days recorded: {len(list_days())}")
        self.__unsaved_days.set(create_date_selection_for_unsaved_sessions())

    @property
    def users_all(self):
        """
        Returns the total number of users.

        Returns:
            int: The total number of users.
        """
        return self.__users_all.get()

    @property
    def users_today(self):
        """
        Returns the number of users for today.

        Returns:
            str: The number of users for today.
        """
        return self.__users_today.get()

    @property
    def sessions_all(self):
        """
        Returns the total number of sessions.

        Returns:
            int: The total number of sessions.
        """
        return self.__sessions_all.get()

    @property
    def days_all(self):
        """
        Returns the total number of days recorded.

        Returns:
            str: The total number of days recorded.
        """
        return self.__days_all.get()

    @property
    def unsaved_days(self):
        """
        Returns the unsaved days.

        Returns:
            list: The unsaved days.
        """
        return self.__unsaved_days.get()

    @property
    def save_view_state(self):
        """
        Gets or sets the save view state.

        Returns:
            bool: The save view state.
        """
        return self.__save_view_state.get()

    @save_view_state.setter
    def save_view_state(self, value):
        self.__save_view_state.set(value)