from __future__ import annotations

from collections.abc import Coroutine
from datetime import datetime, timedelta
from typing import Any, Generic

from cachetory.backends.sync.memory import MemoryBackend as SyncMemoryBackend
from cachetory.interfaces.backends.async_ import AsyncBackend
from cachetory.interfaces.backends.private import WireT
from cachetory.private.asyncio import postpone


class MemoryBackend(AsyncBackend[WireT], Generic[WireT]):
    """Memory backend that stores everything in a local dictionary."""

    __slots__ = ("_inner",)

    @classmethod
    def from_url(cls, _url: str) -> MemoryBackend[WireT]:
        return MemoryBackend()

    def __init__(self) -> None:
        # We'll simply delegate call to the wrapped backend.
        self._inner: SyncMemoryBackend[WireT] = SyncMemoryBackend()

    def get(self, key: str) -> Coroutine[Any, Any, WireT]:
        return postpone(self._inner.get, key)

    def expire_at(self, key: str, deadline: datetime | None) -> Coroutine[Any, Any, None]:
        return postpone(self._inner.expire_at, key, deadline)

    def set(  # noqa: A003
        self,
        key: str,
        value: WireT,
        *,
        time_to_live: timedelta | None = None,
        if_not_exists: bool = False,
    ) -> Coroutine[Any, Any, bool]:
        return postpone(
            self._inner.set,
            key,
            value,
            time_to_live=time_to_live,
            if_not_exists=if_not_exists,
        )

    def delete(self, key: str) -> Coroutine[Any, Any, bool]:
        return postpone(self._inner.delete, key)

    def delete_many(self, *keys: str) -> Coroutine[Any, Any, None]:
        return postpone(self._inner.delete_many, *keys)

    def clear(self) -> Coroutine[Any, Any, None]:
        return postpone(self._inner.clear)

    @property
    def size(self) -> int:
        return self._inner.size
