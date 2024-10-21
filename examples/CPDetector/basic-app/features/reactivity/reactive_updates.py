from features.functions import get_recorded_people_in_total, get_recorded_people_for_a_specific_day, \
    get_all_recorded_sessions_so_far, get_recorded_days, create_date_selection_for_unsaved_sessions
from features.reactivity.reactive_values import users_all, users_today, sessions_all, days_all, unsaved_days


def update_ui():
    users_all.set(len(get_recorded_people_in_total()))
    users_today.set(f"Today: {len(get_recorded_people_for_a_specific_day())}")
    sessions_all.set(len(get_all_recorded_sessions_so_far()))
    days_all.set(f"Days recorded: {len(get_recorded_days())}")
    unsaved_days.set(create_date_selection_for_unsaved_sessions())
