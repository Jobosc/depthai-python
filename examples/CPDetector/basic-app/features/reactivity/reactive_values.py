import datetime

from shiny import reactive

from features.file_operations.read import list_days, list_people_for_a_specific_day, \
    list_people_in_total, list_sessions_in_total, create_date_selection_for_unsaved_sessions

# Variables to display stored data
users_all = reactive.Value(len(list_people_in_total()))
users_today = reactive.Value(
    f"Today: {len(list_people_for_a_specific_day())}"
)
sessions_all = reactive.Value(len(list_sessions_in_total()))
days_all = reactive.Value(f"Days recorded: {len(list_days())}")
unsaved_days = reactive.Value(create_date_selection_for_unsaved_sessions())
save_view_state = reactive.Value(False)

session_view_state = reactive.Value(False)
recording_view_state = reactive.Value(False)
record_button_state = reactive.Value(False)
start_time = reactive.Value(datetime.datetime.now())

hard_drive_state = reactive.Value(False)
camera_state = reactive.Value(False)
camera_led = reactive.Value(None)
