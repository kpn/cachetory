from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timedelta
from typing import Generic

from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.backends.sync import SyncBackend


class DummyBackend(SyncBackend[WireT], Generic[WireT]):
    """Dummy backend that stores nothing."""

    @classmethod
    def from_url(cls, url: str) -> DummyBackend[WireT]:
        return DummyBackend()

    def get(self, key: str) -> WireT:  # pragma: no cover
        raise KeyError(key)

    def get_many(self, *keys: str) -> Iterable[tuple[str, WireT]]:  # pragma: no cover
        return []

    def expire_in(self, key: str, time_to_live: timedelta | None = None) -> None:  # pragma: no cover
        return None

    def expire_at(self, key: str, deadline: datetime | None) -> None:  # pragma: no cover
        return None

    def set(  # noqa: A003
        self,
        key: str,
        value: WireT,
        *,
        time_to_live: timedelta | None = None,
        if_not_exists: bool = False,
    ) -> bool:  # pragma: no cover
        return True

    def set_many(self, items: Iterable[tuple[str, WireT]]) -> None:  # pragma: no cover
        return None

    def delete(self, key: str) -> bool:  # pragma: no cover
        return False  # has never been there

    def delete_many(self, *keys: str) -> None:  # pragma: no cover
        pass

    def clear(self) -> None:  # pragma: no cover
        return None  # already perfectly clean
