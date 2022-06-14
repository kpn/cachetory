from __future__ import annotations

from datetime import datetime, timedelta
from typing import Generic, Iterable, Optional, Tuple

from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.backends.sync import SyncBackend


class DummyBackend(SyncBackend[WireT], Generic[WireT]):
    """
    Dummy backend that stores nothing.
    """

    @classmethod
    def from_url(cls, url: str) -> DummyBackend:
        return DummyBackend()

    def get(self, key: str) -> WireT:  # pragma: no cover
        raise KeyError(key)

    def get_many(self, *keys: str) -> Iterable[Tuple[str, WireT]]:  # pragma: no cover
        return []

    def expire_in(self, key: str, time_to_live: Optional[timedelta] = None) -> None:  # pragma: no cover
        return None

    def expire_at(self, key: str, deadline: Optional[datetime]) -> None:  # pragma: no cover
        return None

    def set(
        self,
        key: str,
        value: WireT,
        *,
        time_to_live: Optional[timedelta] = None,
        if_not_exists: bool = False,
    ) -> bool:  # pragma: no cover
        return True

    def set_many(self, items: Iterable[Tuple[str, WireT]]) -> None:  # pragma: no cover
        return None

    def delete(self, key: str) -> bool:  # pragma: no cover
        return False  # has never been there

    def clear(self) -> None:  # pragma: no cover
        return None  # already perfectly clean
