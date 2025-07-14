from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timedelta
from typing import Generic, cast
from urllib.parse import urlparse

from django.core.cache import BaseCache, cache, caches  # type: ignore[import-untyped]
from django.core.cache.backends.base import DEFAULT_TIMEOUT  # type: ignore[import-untyped]

from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.backends.sync import SyncBackend
from cachetory.private.datetime import make_time_to_live

_SENTINEL = object()


class DjangoBackend(SyncBackend[WireT], Generic[WireT]):
    """Synchronous Django cache adapter."""

    __slots__ = ("_cache",)

    @classmethod
    def from_url(cls, url: str) -> DjangoBackend[WireT]:
        return DjangoBackend(caches[urlparse(url).hostname])

    def __init__(self, cache: BaseCache = cache) -> None:
        """Initialize backend with the Django cache instance."""
        self._cache = cache

    def get(self, key: str) -> WireT:
        if (value := self._cache.get(key, _SENTINEL)) is not _SENTINEL:
            return value  # type: ignore[no-any-return]
        raise KeyError(key)

    def get_many(self, *keys: str) -> Iterable[tuple[str, WireT]]:
        return self._cache.get_many(keys).items()  # type: ignore[no-any-return]

    def set(  # noqa: A003
        self,
        key: str,
        value: WireT,
        *,
        time_to_live: timedelta | None = None,
        if_not_exists: bool = False,
    ) -> bool:
        timeout = self._to_timeout(time_to_live)
        if if_not_exists:
            return cast(bool, self._cache.add(key, value, timeout))
        else:
            self._cache.set(key, value, timeout)
            return True

    def set_many(self, items: Iterable[tuple[str, WireT]]) -> None:
        self._cache.set_many(dict(items))

    def delete(self, key: str) -> bool:
        return self._cache.delete(key)  # type: ignore[no-any-return]

    def delete_many(self, *keys: str) -> None:
        self._cache.delete_many(keys)

    def clear(self) -> None:
        self._cache.clear()

    def expire_in(self, key: str, time_to_live: timedelta | None = None) -> None:
        self._cache.touch(key, self._to_timeout(time_to_live))

    def expire_at(self, key: str, deadline: datetime | None) -> None:
        self.expire_in(key, make_time_to_live(deadline))

    @staticmethod
    def _to_timeout(time_to_live: timedelta | None) -> object:
        return time_to_live.total_seconds() if time_to_live is not None else DEFAULT_TIMEOUT
