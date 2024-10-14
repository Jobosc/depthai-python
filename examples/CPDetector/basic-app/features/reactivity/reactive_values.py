import datetime
import faicons as fa

from shiny import reactive

from features.functions import (
    get_recorded_people_in_total,
    get_recorded_people_for_a_specific_day,
    get_all_recorded_sessions_so_far,
    get_recorded_days, create_date_selection_for_unsaved_sessions,
)

# Variables to display stored data
users_all = reactive.Value(len(get_recorded_people_in_total()))
users_today = reactive.Value(
    f"Today: {len(get_recorded_people_for_a_specific_day())}"
)
sessions_all = reactive.Value(len(get_all_recorded_sessions_so_far()))
days_all = reactive.Value(f"Days recorded: {len(get_recorded_days())}")
unsaved_days = reactive.Value(create_date_selection_for_unsaved_sessions())
save_view_state = reactive.Value(False)

session_view_state = reactive.Value(False)
recording_view_state = reactive.Value(False)
record_button_state = reactive.Value(False)
start_time = reactive.Value(datetime.datetime.now())

hard_drive_state = reactive.Value(False)
camera_state = reactive.Value(False)
camera_led = reactive.Value(None)
