"""
Async cache backend protocol descriptors.

Note, that some methods provide reasonable default implementation,
but implementors SHOULD override them for the sake of performance.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional, Tuple

from typing_extensions import Protocol

from cachetory.interfaces.backends.private import T_wire, T_wire_contra, T_wire_cov


class AsyncBackendRead(Protocol[T_wire_cov]):
    """
    Describes the read operations of an asynchronous cache.
    """

    async def get(self, key: str) -> T_wire_cov:
        """
        Retrieve a value from the cache.

        Returns:
            Cached value, if it exists.
        Raises:
            KeyError: the key doesn't exist in the cache.
        """
        raise NotImplementedError

    async def get_many(self, *keys: str) -> Iterable[Tuple[str, T_wire_cov]]:
        """
        Get all the values corresponding to the specified keys.

        Returns:
            Existing key-value pairs.
        """
        entries = []
        for key in keys:
            try:
                value = await self.get(key)
            except KeyError:
                pass
            else:
                entries.append((key, value))
        return entries


class AsyncBackendWrite(Protocol[T_wire_contra]):
    """
    Describes the write operations of an asynchronous cache.
    """

    async def expire_in(self, key: str, time_to_live: Optional[timedelta] = None) -> None:
        """
        Set the expiration time on the key.
        """
        deadline = datetime.now(timezone.utc) + time_to_live if time_to_live is not None else None
        await self.expire_at(key, deadline)

    async def expire_at(self, key: str, deadline: Optional[datetime]) -> None:
        """
        Set the expiration deadline on the key.
        """
        raise NotImplementedError

    async def set(
        self,
        key: str,
        value: T_wire_contra,
        *,
        time_to_live: Optional[timedelta] = None,
        if_not_exists: bool = False,
    ) -> None:
        """
        Put the value into the cache.
        """
        raise NotImplementedError

    async def set_many(self, items: Iterable[Tuple[str, T_wire_contra]]) -> None:
        """
        Put all the specified values to the cache.
        """
        for (key, value) in items:
            await self.set(key, value)

    async def delete(self, key: str) -> bool:
        """
        Delete the key from the cache.

        Returns:
            `True` if the key has existed, `False` otherwise.
        """
        raise NotImplementedError

    async def clear(self) -> None:
        """
        Clears the backend storage.
        """
        raise NotImplementedError


class AsyncBackend(AsyncBackendRead[T_wire], AsyncBackendWrite[T_wire], Protocol[T_wire]):
    """
    Generic asynchronous cache backend.
    """

    @classmethod
    async def from_url(cls, url: str) -> AsyncBackend:
        raise NotImplementedError
