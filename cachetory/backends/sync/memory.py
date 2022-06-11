from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Generic, Optional

from cachetory.interfaces.backends.shared import T_wire
from cachetory.interfaces.backends.sync import SyncBackend
from cachetory.private.datetime import make_deadline


class SyncMemoryBackend(Generic[T_wire], SyncBackend[T_wire]):
    __slots__ = ("_entries",)

    @classmethod
    def from_url(cls, _url: str) -> SyncMemoryBackend:
        return SyncMemoryBackend()

    def __init__(self):
        self._entries: Dict[str, _Entry[T_wire]] = {}

    def get(self, key: str) -> T_wire:
        return self._get_entry(key).value

    def expire_at(self, key: str, deadline: Optional[datetime]) -> None:
        try:
            entry = self._get_entry(key)
        except KeyError:
            pass
        else:
            entry.deadline = deadline

    def set(
        self,
        key: str,
        value: T_wire,
        *,
        time_to_live: Optional[timedelta] = None,
        if_not_exists: bool = False,
    ) -> None:
        entry = _Entry[T_wire](value, make_deadline(time_to_live))
        if if_not_exists:
            self._entries.setdefault(key, entry)
        else:
            self._entries[key] = _Entry[T_wire](value, make_deadline(time_to_live))

    def delete(self, key: str) -> bool:
        return self._entries.pop(key, _SENTINEL) is not _SENTINEL

    def clear(self) -> None:
        self._entries.clear()

    def _get_entry(self, key: str) -> _Entry[T_wire]:
        entry = self._entries[key]
        if entry.deadline is not None and entry.deadline <= datetime.now(timezone.utc):
            self._entries.pop(key, None)  # might get popped by another thread
            raise KeyError(f"`{key}` has expired")
        return entry

    @property
    def size(self) -> int:
        return len(self._entries)


class _Entry(Generic[T_wire]):
    """
    `mypy` doesn't support generic named tuples, thus defining this little one.
    """

    value: T_wire
    deadline: Optional[datetime]

    __slots__ = ("value", "deadline")

    def __init__(self, value: T_wire, deadline: Optional[datetime]):
        self.value = value
        self.deadline = deadline


_SENTINEL = object()
