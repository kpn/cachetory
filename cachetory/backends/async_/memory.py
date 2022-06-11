from datetime import datetime, timedelta
from typing import Any, Coroutine, Generic, Optional

from cachetory.backends.sync.memory import SyncMemoryBackend
from cachetory.interfaces.backends.async_ import AsyncBackendRead, AsyncBackendWrite
from cachetory.interfaces.backends.shared import T_wire
from cachetory.private.asyncio import postpone


class AsyncMemoryBackend(Generic[T_wire], AsyncBackendRead[T_wire], AsyncBackendWrite[T_wire]):
    __slots__ = ("_backend",)

    def __init__(self):
        # We'll simply delegate call to the wrapped backend.
        self._backend = SyncMemoryBackend()

    def get(self, key: str) -> Coroutine[Any, Any, T_wire]:
        return postpone(self._backend.get, key)

    def expire_at(self, key: str, deadline: Optional[datetime]) -> Coroutine[Any, Any, None]:
        return postpone(self._backend.expire_at, key, deadline)

    def set(
        self,
        key: str,
        value: T_wire,
        *,
        time_to_live: Optional[timedelta] = None,
        if_not_exists: bool = False,
    ) -> Coroutine[Any, Any, None]:
        return postpone(
            self._backend.set,
            key,
            value,
            time_to_live=time_to_live,
            if_not_exists=if_not_exists,
        )

    def delete(self, key: str) -> Coroutine[Any, Any, bool]:
        return postpone(self._backend.delete, key)

    def clear(self) -> Coroutine[Any, Any, None]:
        return postpone(self._backend.clear)

    @property
    def size(self) -> int:
        return self._backend.size
