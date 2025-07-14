from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Generic

from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.backends.sync import SyncBackend
from cachetory.private.datetime import make_deadline


class MemoryBackend(SyncBackend[WireT], Generic[WireT]):
    """Memory backend that stores everything in a local dictionary."""

    __slots__ = ("_entries",)

    @classmethod
    def from_url(cls, _url: str) -> MemoryBackend[WireT]:
        return MemoryBackend()

    def __init__(self) -> None:
        self._entries: dict[str, _Entry[WireT]] = {}

    def get(self, key: str) -> WireT:
        return self._get_entry(key).value

    def expire_at(self, key: str, deadline: datetime | None) -> None:
        try:
            entry = self._get_entry(key)
        except KeyError:
            pass
        else:
            entry.deadline = deadline

    def set(  # noqa: A003
        self,
        key: str,
        value: WireT,
        *,
        time_to_live: timedelta | None = None,
        if_not_exists: bool = False,
    ) -> bool:
        entry = _Entry[WireT](value, make_deadline(time_to_live))
        if if_not_exists:
            return self._entries.setdefault(key, entry) is entry
        else:
            self._entries[key] = _Entry[WireT](value, make_deadline(time_to_live))
            return True

    def delete(self, key: str) -> bool:
        return self._entries.pop(key, _SENTINEL) is not _SENTINEL

    def delete_many(self, *keys: str) -> None:
        for key in keys:
            self._entries.pop(key, None)

    def clear(self) -> None:
        self._entries.clear()

    def _get_entry(self, key: str) -> _Entry[WireT]:
        entry = self._entries[key]
        if entry.deadline is not None and entry.deadline <= datetime.now(timezone.utc):
            self._entries.pop(key, None)  # might get popped by another thread
            raise KeyError(f"`{key}` has expired")
        return entry

    @property
    def size(self) -> int:
        return len(self._entries)


class _Entry(Generic[WireT]):
    """`mypy` doesn't support generic named tuples, thus defining this little one."""

    value: WireT
    deadline: datetime | None

    __slots__ = ("value", "deadline")

    def __init__(self, value: WireT, deadline: datetime | None) -> None:
        self.value = value
        self.deadline = deadline


_SENTINEL = object()
