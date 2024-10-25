import logging

from shiny import reactive

from features.file_operations.read import list_days, list_people_for_a_specific_day, \
    list_people_in_total, list_sessions_in_total, create_date_selection_for_unsaved_sessions


class UIState:
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

    def update_ui(self):
        self.__users_all.set(len(list_people_in_total()))
        self.__users_today.set(f"Today: {len(list_people_for_a_specific_day())}")
        self.__sessions_all.set(len(list_sessions_in_total()))
        self.__days_all.set(f"Days recorded: {len(list_days())}")
        self.__unsaved_days.set(create_date_selection_for_unsaved_sessions())

    @property
    def users_all(self):
        return self.__users_all.get()

    @property
    def users_today(self):
        return self.__users_today.get()

    @property
    def sessions_all(self):
        return self.__sessions_all.get()

    @property
    def days_all(self):
        return self.__days_all.get()

    @property
    def unsaved_days(self):
        return self.__unsaved_days.get()

    @property
    def save_view_state(self):
        return self.__save_view_state.get()

    @save_view_state.setter
    def save_view_state(self, value):
        self.__save_view_state.set(value)
