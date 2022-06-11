from __future__ import annotations

from datetime import datetime, timedelta
from typing import Generic, Iterable, Optional, Tuple

from cachetory.interfaces.backends.async_ import AsyncBackend
from cachetory.interfaces.backends.private import T_wire


class AsyncDummyBackend(Generic[T_wire], AsyncBackend[T_wire]):
    @classmethod
    async def from_url(cls, url: str) -> AsyncDummyBackend:
        return AsyncDummyBackend()

    async def get(self, key: str) -> T_wire:
        raise KeyError(key)

    async def get_many(self, *keys: str) -> Iterable[Tuple[str, T_wire]]:
        return []

    async def expire_in(self, key: str, time_to_live: Optional[timedelta] = None) -> None:
        return None

    async def expire_at(self, key: str, deadline: Optional[datetime]) -> None:
        return None

    async def set(
        self,
        key: str,
        value: T_wire,
        *,
        time_to_live: Optional[timedelta] = None,
        if_not_exists: bool = False,
    ) -> None:
        return None

    async def set_many(self, items: Iterable[Tuple[str, T_wire]]) -> None:
        return None

    async def delete(self, key: str) -> bool:
        return False  # has never been there

    async def clear(self) -> None:
        return None  # already perfectly clean
