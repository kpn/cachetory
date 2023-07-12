from datetime import datetime, timedelta, timezone

from cachetory.private.datetime import ZERO_TIMEDELTA, make_time_to_live


def test_make_time_to_live_none() -> None:
    assert make_time_to_live(None) is None


def test_make_time_to_live_negative() -> None:
    assert make_time_to_live(datetime.now(timezone.utc) - timedelta(seconds=10.0)) == ZERO_TIMEDELTA


def test_make_time_to_live_positive() -> None:
    time_to_live = make_time_to_live(datetime.now(timezone.utc) + timedelta(seconds=10.0))
    assert time_to_live is not None
    assert time_to_live > ZERO_TIMEDELTA
