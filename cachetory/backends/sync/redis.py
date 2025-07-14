from __future__ import annotations

import itertools
from collections.abc import Iterable
from datetime import datetime, timedelta
from types import TracebackType

from redis import Redis

from cachetory.interfaces.backends.sync import SyncBackend


class RedisBackend(SyncBackend[bytes]):
    """Synchronous Redis backend."""

    __slots__ = ("_client",)

    @classmethod
    def from_url(cls, url: str) -> RedisBackend:
        """Instantiate a backend from the URL."""
        if url.startswith("redis+"):
            url = url[6:]
        return cls(Redis.from_url(url))

    def __init__(self, client: Redis) -> None:  # type: ignore[type-arg]
        """Instantiate a backend using the Redis client."""
        self._client = client

    def get(self, key: str) -> bytes:
        data: bytes | None = self._client.get(key)
        if data is not None:
            return data
        raise KeyError(key)

    def get_many(self, *keys: str) -> Iterable[tuple[str, bytes]]:
        for key, value in zip(keys, self._client.mget(*keys)):
            if value is not None:
                yield key, value

    def expire_at(self, key: str, deadline: datetime | None) -> None:
        if deadline:
            # One can pass `datetime` directly to `pexpireat`, but the latter
            # incorrectly converts datetime into timestamp.
            self._client.pexpireat(key, int(deadline.timestamp() * 1000.0))
        else:
            self._client.persist(key)

    def expire_in(self, key: str, time_to_live: timedelta | None = None) -> None:
        if time_to_live:
            self._client.pexpire(key, time_to_live)
        else:
            self._client.persist(key)

    def set(  # noqa: A003
        self,
        key: str,
        value: bytes,
        *,
        time_to_live: timedelta | None = None,
        if_not_exists: bool = False,
    ) -> bool:
        return bool(self._client.set(key, value, px=time_to_live, nx=if_not_exists))

    def set_many(self, items: Iterable[tuple[str, bytes]]) -> None:
        self._client.execute_command("MSET", *itertools.chain.from_iterable(items))

    def delete(self, key: str) -> bool:
        return bool(self._client.delete(key))

    def delete_many(self, *keys: str) -> None:
        if keys:
            self._client.delete(*keys)

    def clear(self) -> None:
        self._client.flushdb()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return self._client.__exit__(exc_type, exc_value, traceback)
