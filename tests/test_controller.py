"""Tests du contrôleur HorlogeController."""

from __future__ import annotations

from horloge_jdr.controller import HorlogeController
from horloge_jdr.domain import DisplayMode


def test_controller_notifies_listeners_on_plus_hour() -> None:
    controller = HorlogeController()
    received: list = []
    controller.add_listener(lambda s: received.append(s))

    controller.on_plus_hour()

    assert len(received) == 1
    assert received[0].current_display_text() == "01:00"


def test_controller_notifies_listeners_on_minus_hour() -> None:
    controller = HorlogeController()
    controller.on_plus_hour()
    received: list = []
    controller.add_listener(lambda s: received.append(s))

    controller.on_minus_hour()

    assert len(received) == 1
    assert received[0].current_display_text() == "00:00"


def test_controller_notifies_listeners_on_time_changes() -> None:
    controller = HorlogeController()
    received: list = []
    controller.add_listener(lambda s: received.append(s.current_display_text()))

    controller.on_plus_10min()
    controller.on_plus_10min()

    assert len(received) == 2
    assert received[0] == "00:10"
    assert received[1] == "00:20"


def test_controller_notifies_listeners_on_day_changes() -> None:
    controller = HorlogeController()
    received: list = []
    controller.add_listener(lambda s: received.append(s.current_day_text()))

    controller.on_plus_day()
    controller.on_plus_day()

    assert len(received) == 2
    assert received[0] == "Jour 1"
    assert received[1] == "Jour 2"


def test_controller_listener_can_be_removed() -> None:
    controller = HorlogeController()
    received: list = []

    def listener(state):
        received.append(state)

    controller.add_listener(listener)
    controller.on_plus_hour()
    assert len(received) == 1

    controller.remove_listener(listener)
    controller.on_plus_hour()
    assert len(received) == 1


def test_controller_set_display_message_notifies() -> None:
    controller = HorlogeController()
    received: list = []
    controller.add_listener(lambda s: received.append(s))

    controller.on_set_display_message("Hello")
    controller.on_set_display_message_right("Right")

    assert len(received) == 2
    assert received[0].display_message == "Hello"
    assert received[1].display_message_right == "Right"


def test_controller_display_mode_change_notifies() -> None:
    controller = HorlogeController()
    received: list = []
    controller.add_listener(lambda s: received.append(s))

    controller.on_start_countdown(5)
    controller.on_set_display_countdown()

    assert len(received) >= 2
    assert controller.state.display_mode is DisplayMode.COUNTDOWN
    assert controller.state.current_display_text().startswith("05:")
