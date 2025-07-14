from __future__ import annotations

import itertools
from collections.abc import AsyncIterable, Iterable
from datetime import datetime, timedelta
from types import TracebackType

from redis.asyncio import Redis

from cachetory.interfaces.backends.async_ import AsyncBackend


class RedisBackend(AsyncBackend[bytes]):
    """Asynchronous Redis backend."""

    __slots__ = ("_client",)

    @classmethod
    def from_url(cls, url: str) -> RedisBackend:
        """Instantiate a backend from the URL."""
        if url.startswith("redis+"):
            url = url[6:]
        return RedisBackend(Redis.from_url(url))

    def __init__(self, client: Redis) -> None:  # type: ignore[type-arg]
        """Instantiate a backend using the Redis client."""
        self._client = client

    async def get(self, key: str) -> bytes:
        data: bytes | None = await self._client.get(key)
        if data is not None:
            return data
        raise KeyError(key)

    async def get_many(self, *keys: str) -> AsyncIterable[tuple[str, bytes]]:
        for key, value in zip(keys, await self._client.mget(*keys)):
            if value is not None:
                yield key, value

    async def expire_at(self, key: str, deadline: datetime | None) -> None:
        if deadline:
            # One can pass `datetime` directly to `pexpireat`, but the latter
            # incorrectly converts datetime into timestamp.
            await self._client.pexpireat(key, int(deadline.timestamp() * 1000.0))
        else:
            await self._client.persist(key)

    async def expire_in(self, key: str, time_to_live: timedelta | None = None) -> None:
        if time_to_live:
            await self._client.pexpire(key, time_to_live)
        else:
            await self._client.persist(key)

    async def set(  # noqa: A003
        self,
        key: str,
        value: bytes,
        *,
        time_to_live: timedelta | None = None,
        if_not_exists: bool = False,
    ) -> bool:
        return bool(await self._client.set(key, value, px=time_to_live, nx=if_not_exists))

    async def set_many(self, items: Iterable[tuple[str, bytes]]) -> None:
        await self._client.execute_command("MSET", *itertools.chain.from_iterable(items))

    async def delete(self, key: str) -> bool:
        return bool(await self._client.delete(key))

    async def delete_many(self, *keys: str) -> None:
        if keys:
            await self._client.delete(*keys)

    async def clear(self) -> None:
        await self._client.flushdb()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self._client.connection_pool.disconnect()  # https://github.com/aio-libs/aioredis-py/issues/1103
        return await self._client.__aexit__(exc_type, exc_value, traceback)
