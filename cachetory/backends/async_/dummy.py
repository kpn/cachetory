from __future__ import annotations

from datetime import datetime, timedelta
from typing import AsyncIterable, Generic, Iterable, Optional, Tuple

from cachetory.interfaces.backends.async_ import AsyncBackend
from cachetory.interfaces.backends.private import WireT


class DummyBackend(AsyncBackend[WireT], Generic[WireT]):
    """
    Dummy backend that stores nothing.
    """

    @classmethod
    def from_url(cls, url: str) -> DummyBackend:
        return DummyBackend()

    async def get(self, key: str) -> WireT:  # pragma: no cover
        raise KeyError(key)

    async def get_many(self, *keys: str) -> AsyncIterable[Tuple[str, WireT]]:
        for _ in ():  # pragma: no cover
            yield ()  # type: ignore

    async def expire_in(self, key: str, time_to_live: Optional[timedelta] = None) -> None:  # pragma: no cover
        return None

    async def expire_at(self, key: str, deadline: Optional[datetime]) -> None:  # pragma: no cover
        return None

    async def set(
        self,
        key: str,
        value: WireT,
        *,
        time_to_live: Optional[timedelta] = None,
        if_not_exists: bool = False,
    ) -> bool:  # pragma: no cover
        return True

    async def set_many(self, items: Iterable[Tuple[str, WireT]]) -> None:  # pragma: no cover
        return None

    async def delete(self, key: str) -> bool:  # pragma: no cover
        return False  # has never been there

    async def clear(self) -> None:  # pragma: no cover
        return None  # already perfectly clean
