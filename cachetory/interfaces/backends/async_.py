"""
Async cache backend protocol descriptors.

Note, that some methods provide reasonable default implementation,
but implementors SHOULD override them for the sake of performance.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from contextlib import AbstractAsyncContextManager
from datetime import datetime, timedelta, timezone
from typing import AsyncIterable, Generic, Iterable, Optional, Tuple

from typing_extensions import Protocol

from cachetory.interfaces.backends.private import WireT, WireT_co, WireT_contra


class AsyncBackendRead(Protocol[WireT_co]):
    """
    Describes the read operations of an asynchronous cache.
    """

    async def get(self, key: str) -> WireT_co:  # pragma: no cover
        """
        Retrieve a value from the cache.

        Returns:
            Cached value, if it exists.
        Raises:
            KeyError: the key doesn't exist in the cache.
        """
        raise NotImplementedError

    async def get_many(self, *keys: str) -> AsyncIterable[Tuple[str, WireT_co]]:
        """
        Get all the values corresponding to the specified keys.

        Returns:
            Existing key-value pairs.
        """
        for key in keys:
            try:
                value = await self.get(key)
            except KeyError:
                pass
            else:
                yield key, value


class AsyncBackendWrite(Protocol[WireT_contra]):
    """
    Describes the write operations of an asynchronous cache.
    """

    async def expire_in(self, key: str, time_to_live: Optional[timedelta] = None) -> None:
        """
        Set the expiration time on the key.
        """
        deadline = datetime.now(timezone.utc) + time_to_live if time_to_live is not None else None
        await self.expire_at(key, deadline)

    async def expire_at(self, key: str, deadline: Optional[datetime]) -> None:  # pragma: no cover
        """
        Set the expiration deadline on the key.
        """
        raise NotImplementedError

    async def set(
        self,
        key: str,
        value: WireT_contra,
        *,
        time_to_live: Optional[timedelta] = None,
        if_not_exists: bool = False,
    ) -> bool:  # pragma: no cover
        """
        Put the value into the cache.

        Returns:
            `True` if the value has been successfully set, `False` when `if_not_exists` is true
            and the key is already existing.
        """
        raise NotImplementedError

    async def set_many(self, items: Iterable[Tuple[str, WireT_contra]]) -> None:
        """
        Put all the specified values to the cache.
        """
        for (key, value) in items:
            await self.set(key, value)

    async def delete(self, key: str) -> bool:  # pragma: no cover
        """
        Delete the key from the cache.

        Returns:
            `True` if the key has existed, `False` otherwise.
        """
        raise NotImplementedError

    async def clear(self) -> None:  # pragma: no cover
        """
        Clears the backend storage.
        """
        raise NotImplementedError


class AsyncBackend(
    AbstractAsyncContextManager,
    AsyncBackendRead[WireT],
    AsyncBackendWrite[WireT],
    Generic[WireT],
    metaclass=ABCMeta,
):
    """
    Generic asynchronous cache backend.
    """

    @classmethod
    @abstractmethod
    def from_url(cls, url: str) -> AsyncBackend:  # pragma: no cover
        """
        Create an asynchronous cache backend from the specified URL.

        Returns:
            An instance of the specific backend class.
        """
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        return None
