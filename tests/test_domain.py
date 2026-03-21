from __future__ import annotations

from horloge_jdr.domain import AppState, ClockState, CountdownModel, DisplayMode
from horloge_jdr.time_model import TimeModel, DayCounter


def test_time_model_wraps_around_day() -> None:
    model = TimeModel(total_minutes=(23 * 60) + 50)
    model.add_minutes(20)
    assert model.hours == 0
    assert model.minutes == 10


def test_clock_state_changes_day_forward_and_backward() -> None:
    clock = ClockState(time_model=TimeModel(total_minutes=(23 * 60) + 50), day_counter=DayCounter(days=0))

    clock.add_minutes(20)
    assert clock.time_model.formatted() == "00:10"
    assert clock.day_counter.days == 1

    clock.add_minutes(-20)
    assert clock.time_model.formatted() == "23:50"
    assert clock.day_counter.days == 0


def test_countdown_model_basic_flow() -> None:
    countdown = CountdownModel()

    countdown.start(1)
    assert countdown.running is True
    assert countdown.remaining_seconds == 60

    for _ in range(60):
        countdown.tick_one_second()

    assert countdown.remaining_seconds == 0
    assert countdown.running is False
    assert countdown.formatted_mm_ss() == "00:00"


def test_app_state_display_mode_and_texts() -> None:
    state = AppState()

    assert state.display_mode is DisplayMode.MANUAL_TIME
    assert state.current_display_text() == "00:00"
    assert state.current_day_text().startswith("Jour")

    state.start_countdown(2)
    state.set_display_mode(DisplayMode.COUNTDOWN)
    assert state.current_display_text().startswith("02:")


def test_app_state_display_message() -> None:
    state = AppState()
    assert state.display_message == ""

    state.set_display_message("Ligne 1\nLigne 2")
    assert state.display_message == "Ligne 1\nLigne 2"

    state.set_display_message("a\r\nb")
    assert state.display_message == "a\nb"


def test_app_state_display_message_right() -> None:
    state = AppState()
    assert state.display_message_right == ""
    state.set_display_message_right("Note")
    assert state.display_message_right == "Note"

