from __future__ import annotations

from collections.abc import AsyncIterable, Iterable
from datetime import datetime, timedelta
from typing import Generic, cast
from urllib.parse import urlparse

from django.core.cache import BaseCache, cache, caches  # type: ignore[import-untyped]
from django.core.cache.backends.base import DEFAULT_TIMEOUT  # type: ignore[import-untyped]

from cachetory.interfaces.backends.async_ import AsyncBackend
from cachetory.interfaces.backends.private import WireT
from cachetory.private.datetime import make_time_to_live

_SENTINEL = object()


class DjangoBackend(AsyncBackend[WireT], Generic[WireT]):
    """Asynchronous Django cache adapter."""

    __slots__ = ("_cache",)

    @classmethod
    def from_url(cls, url: str) -> DjangoBackend[WireT]:
        return DjangoBackend(caches[urlparse(url).hostname])

    def __init__(self, cache: BaseCache = cache) -> None:
        """Initialize backend with the Django cache instance."""
        self._cache = cache

    async def get(self, key: str) -> WireT:
        if (value := await self._cache.aget(key, _SENTINEL)) is not _SENTINEL:
            return value  # type: ignore[no-any-return]
        raise KeyError(key)

    async def get_many(self, *keys: str) -> AsyncIterable[tuple[str, WireT]]:
        for item in (await self._cache.aget_many(keys)).items():
            yield item

    async def set(  # noqa: A003
        self,
        key: str,
        value: WireT,
        *,
        time_to_live: timedelta | None = None,
        if_not_exists: bool = False,
    ) -> bool:
        timeout = self._to_timeout(time_to_live)
        if if_not_exists:
            return cast(bool, await self._cache.aadd(key, value, timeout))
        else:
            await self._cache.aset(key, value, timeout)
            return True

    async def set_many(self, items: Iterable[tuple[str, WireT]]) -> None:
        await self._cache.aset_many(dict(items))

    async def delete(self, key: str) -> bool:
        return await self._cache.adelete(key)  # type: ignore[no-any-return]

    async def delete_many(self, *keys: str) -> None:
        await self._cache.adelete_many(keys)

    async def clear(self) -> None:
        await self._cache.aclear()

    async def expire_in(self, key: str, time_to_live: timedelta | None = None) -> None:
        await self._cache.atouch(key, self._to_timeout(time_to_live))

    async def expire_at(self, key: str, deadline: datetime | None) -> None:
        await self.expire_in(key, make_time_to_live(deadline))

    @staticmethod
    def _to_timeout(time_to_live: timedelta | None) -> object:
        return time_to_live.total_seconds() if time_to_live is not None else DEFAULT_TIMEOUT
