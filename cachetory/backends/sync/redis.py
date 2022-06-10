from __future__ import annotations

import itertools
from datetime import datetime, timedelta
from typing import Iterable, Optional, Tuple

import redis

from cachetory.interfaces.backends.sync import SyncBackendRead, SyncBackendWrite


class SyncRedisBackend(SyncBackendRead[bytes], SyncBackendWrite[bytes]):
    @classmethod
    def from_url(cls, url: str) -> SyncRedisBackend:
        return cls(redis.Redis.from_url(url))

    def __init__(self, client: redis.Redis):
        self._client = client

    def get(self, key: str) -> bytes:
        data = self._client.get(key)
        if data:
            return data
        raise KeyError(key)

    def get_many(self, *keys: str) -> Iterable[Tuple[str, bytes]]:
        for key, value in zip(keys, self._client.mget(*keys)):
            if value:
                yield key, value

    def expire_at(self, key: str, deadline: Optional[datetime]) -> None:
        if deadline:
            self._client.pexpireat(key, deadline)
        else:
            self._client.persist(key)

    def expire_in(self, key: str, time_to_live: Optional[timedelta] = None) -> None:
        if time_to_live:
            self._client.pexpire(key, time_to_live)
        else:
            self._client.persist(key)

    def set(
        self,
        key: str,
        value: bytes,
        *,
        time_to_live: Optional[timedelta] = None,
        if_not_exists: bool = False,
    ) -> None:
        self._client.set(key, value, ex=time_to_live, nx=if_not_exists)

    def set_many(self, items: Iterable[Tuple[str, bytes]]) -> None:
        self._client.execute_command("MSET", *itertools.chain.from_iterable(items))

    def delete(self, key: str) -> bool:
        return bool(self._client.delete(key))
