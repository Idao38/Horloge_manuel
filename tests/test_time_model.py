from src.horloge_jdr.time_model import DayCounter, MINUTES_PER_DAY, TimeModel


def test_initial_time_is_zero():
    model = TimeModel()
    assert model.total_minutes == 0
    assert model.formatted() == "00:00"


def test_add_hours_simple():
    model = TimeModel()
    model.add_hours(1)
    assert model.formatted() == "01:00"


def test_add_minutes_simple():
    model = TimeModel()
    model.add_minutes(10)
    assert model.formatted() == "00:10"


def test_add_hours_wraps_past_midnight():
    model = TimeModel(total_minutes=23 * 60)
    model.add_hours(2)
    # 23:00 + 2h = 01:00
    assert model.formatted() == "01:00"


def test_add_minutes_wraps_past_midnight():
    model = TimeModel(total_minutes=23 * 60 + 55)
    model.add_minutes(10)
    # 23:55 + 10 min = 00:05
    assert model.formatted() == "00:05"


def test_subtract_hours_wraps_before_midnight():
    model = TimeModel(total_minutes=30)  # 00:30
    model.add_hours(-1)
    # 00:30 - 1h = 23:30
    assert model.formatted() == "23:30"


def test_subtract_minutes_wraps_before_midnight():
    model = TimeModel(total_minutes=5)  # 00:05
    model.add_minutes(-10)
    # 00:05 - 10 min = 23:55
    assert model.formatted() == "23:55"


def test_total_minutes_always_in_valid_range():
    model = TimeModel(total_minutes=0)
    model.add_minutes(10_000)
    assert 0 <= model.total_minutes < MINUTES_PER_DAY


def test_day_counter_initial_value_is_zero():
    counter = DayCounter()
    assert counter.days == 0
    assert counter.formatted() == "Jour 0"


def test_day_counter_increment_and_decrement():
    counter = DayCounter()
    counter.add_days(1)
    assert counter.days == 1
    counter.add_days(4)
    assert counter.days == 5
    counter.add_days(-2)
    assert counter.days == 3

