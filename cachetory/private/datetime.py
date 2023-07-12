from __future__ import annotations

from datetime import datetime, timedelta, timezone

ZERO_TIMEDELTA = timedelta()


def make_deadline(time_to_live: timedelta | None = None) -> datetime | None:
    return datetime.now(timezone.utc) + time_to_live if time_to_live is not None else None


def make_time_to_live(deadline: datetime | None = None) -> timedelta | None:
    if deadline is None:
        return None
    return max(deadline - datetime.now(timezone.utc), ZERO_TIMEDELTA)
