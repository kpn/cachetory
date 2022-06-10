from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Generic, Optional

from cachetory.interfaces.backends.shared import T_value
from cachetory.interfaces.backends.sync import SyncBackendRead, SyncBackendWrite
from cachetory.private.datetime import make_deadline


class SyncMemoryBackend(Generic[T_value], SyncBackendRead[T_value], SyncBackendWrite[T_value]):
    __slots__ = ("_entries",)

    def __init__(self):
        self._entries: Dict[str, _Entry[T_value]] = {}

    def __getitem__(self, key: str) -> T_value:
        return self._get_entry(key).value

    def expire_at(self, key: str, deadline: Optional[datetime]) -> None:
        try:
            entry = self._get_entry(key)
        except KeyError:
            pass
        else:
            entry.deadline = deadline

    def set(self, key: str, value: T_value, time_to_live: Optional[timedelta] = None) -> None:
        self._entries[key] = _Entry[T_value](value, make_deadline(time_to_live))

    def set_default(self, key: str, value: T_value, time_to_live: Optional[timedelta] = None) -> None:
        entry = _Entry[T_value](value, make_deadline(time_to_live))
        self._entries.setdefault(key, entry)

    def delete(self, key: str) -> bool:
        return self._entries.pop(key, _SENTINEL) is not _SENTINEL

    def __delitem__(self, key: str) -> None:
        del self._entries[key]

    def _get_entry(self, key: str) -> _Entry[T_value]:
        entry = self._entries[key]
        if entry.deadline is not None and entry.deadline <= datetime.now(timezone.utc):
            self._entries.pop(key, None)  # might get popped by another thread
            raise KeyError(f"`{key}` has expired")
        return entry

    @property
    def size(self) -> int:
        return len(self._entries)


class _Entry(Generic[T_value]):
    """
    `mypy` doesn't support generic named tuples, thus defining this little one.
    """

    value: T_value
    deadline: Optional[datetime]

    __slots__ = ("value", "deadline")

    def __init__(self, value: T_value, deadline: Optional[datetime]):
        self.value = value
        self.deadline = deadline


_SENTINEL = object()
