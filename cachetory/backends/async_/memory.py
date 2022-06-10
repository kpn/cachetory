from datetime import datetime, timedelta
from typing import Any, Awaitable, Coroutine, Generic, Optional

from cachetory.backends.sync.memory import SyncMemoryBackend
from cachetory.interfaces.backends.async_ import AsyncBackendRead, AsyncBackendWrite
from cachetory.interfaces.backends.shared import TV
from cachetory.private.asyncio import postpone


class AsyncMemoryBackend(Generic[TV], AsyncBackendRead[TV], AsyncBackendWrite[TV]):
    __slots__ = ("_backend",)

    def __init__(self):
        # We'll simply delegate call to the wrapped backend.
        self._backend = SyncMemoryBackend()

    def __getitem__(self, key: str) -> Awaitable[TV]:
        # We want to retrieve a value when the awaitable gets actually awaited,
        # and that might happen somewhat later allowing the backend to change in the meantime.
        return postpone(self._backend.__getitem__, key)

    def expire_at(self, key: str, deadline: Optional[datetime]) -> Coroutine[Any, Any, None]:
        return postpone(self._backend.expire_at, key, deadline)

    def set(
        self,
        key: str,
        value: TV,
        time_to_live: Optional[timedelta] = None,
    ) -> Coroutine[Any, Any, None]:
        return postpone(self._backend.set, key, value, time_to_live)

    def set_default(
        self,
        key: str,
        value: TV,
        time_to_live: Optional[timedelta] = None,
    ) -> Coroutine[Any, Any, None]:
        return postpone(self._backend.set_default, key, value, time_to_live)

    def delete(self, key: str) -> Coroutine[Any, Any, bool]:
        return postpone(self._backend.delete, key)

    @property
    def size(self) -> int:
        return self._backend.size
