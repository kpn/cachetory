from datetime import datetime, timedelta, timezone
from typing import Optional


def make_deadline(time_to_live: Optional[timedelta] = None) -> Optional[datetime]:
    return datetime.now(timezone.utc) + time_to_live if time_to_live is not None else None
