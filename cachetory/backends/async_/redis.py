from __future__ import annotations

import itertools
from datetime import datetime, timedelta
from typing import AsyncIterable, Iterable, Optional, Tuple

import aioredis

from cachetory.interfaces.backends.async_ import AsyncBackend


class AsyncRedisBackend(AsyncBackend[bytes]):
    __slots__ = ("_client",)

    @classmethod
    async def from_url(cls, url: str) -> AsyncRedisBackend:
        return AsyncRedisBackend(aioredis.Redis.from_url(url))

    def __init__(self, client: aioredis.Redis):
        self._client = client

    async def get(self, key: str) -> bytes:
        data = await self._client.get(key)
        if data:
            return data
        raise KeyError(key)

    async def get_many(self, *keys: str) -> AsyncIterable[Tuple[str, bytes]]:
        for key, value in zip(keys, await self._client.mget(*keys)):
            if value:
                yield key, value

    async def expire_at(self, key: str, deadline: Optional[datetime]) -> None:
        if deadline:
            await self._client.pexpireat(key, deadline)
        else:
            await self._client.persist(key)

    async def expire_in(self, key: str, time_to_live: Optional[timedelta] = None) -> None:
        if time_to_live:
            await self._client.pexpire(key, time_to_live)
        else:
            await self._client.persist(key)

    async def set(
        self,
        key: str,
        value: bytes,
        *,
        time_to_live: Optional[timedelta] = None,
        if_not_exists: bool = False,
    ) -> None:
        await self._client.set(key, value, ex=time_to_live, nx=if_not_exists)

    async def set_many(self, items: Iterable[Tuple[str, bytes]]) -> None:
        await self._client.execute_command("MSET", *itertools.chain.from_iterable(items))

    async def delete(self, key: str) -> bool:
        return bool(await self._client.delete(key))

    async def clear(self) -> None:
        await self._client.flushdb()
