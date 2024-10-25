from features.file_operations.read import list_days, list_people_for_a_specific_day, \
    list_people_in_total, list_sessions_in_total, create_date_selection_for_unsaved_sessions
from features.reactivity.reactive_values import users_all, users_today, sessions_all, days_all, unsaved_days


def update_ui():
    users_all.set(len(list_people_in_total()))
    users_today.set(f"Today: {len(list_people_for_a_specific_day())}")
    sessions_all.set(len(list_sessions_in_total()))
    days_all.set(f"Days recorded: {len(list_days())}")
    unsaved_days.set(create_date_selection_for_unsaved_sessions())
