"""
Async cache backend protocol descriptors.

Note, that some methods provide reasonable default implementation,
but implementors SHOULD override them for the sake of performance.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections.abc import AsyncIterable, Iterable
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from datetime import datetime, timedelta, timezone
from types import TracebackType
from typing import Any, Generic

from typing_extensions import Never, Protocol

from cachetory.interfaces.backends.private import WireT, WireT_co, WireT_contra


class AsyncBackendRead(Protocol[WireT_co]):
    """Describes the read operations of an asynchronous cache."""

    async def get(self, key: str) -> WireT_co:  # pragma: no cover
        """
        Retrieve a value from the cache.

        Returns:
            Cached value, if it exists.

        Raises:
            KeyError: the key doesn't exist in the cache.
        """
        raise NotImplementedError

    async def get_many(self, *keys: str) -> AsyncIterable[tuple[str, WireT_co]]:
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
    """Describes the write operations of an asynchronous cache."""

    async def expire_in(self, key: str, time_to_live: timedelta | None = None) -> None:
        """Set the expiration time on the key."""
        deadline = datetime.now(timezone.utc) + time_to_live if time_to_live is not None else None
        await self.expire_at(key, deadline)

    async def expire_at(self, key: str, deadline: datetime | None) -> None:  # pragma: no cover
        """Set the expiration deadline on the key."""
        raise NotImplementedError

    async def set(  # noqa: A003
        self,
        key: str,
        value: WireT_contra,
        *,
        time_to_live: timedelta | None = None,
        if_not_exists: bool = False,
    ) -> bool:  # pragma: no cover
        """
        Put the value into the cache.

        Returns:
            `True` if the value has been successfully set, `False` when `if_not_exists` is true
            and the key is already existing.
        """

        # TODO: just return `None`.
        raise NotImplementedError

    async def set_many(self, items: Iterable[tuple[str, WireT_contra]]) -> None:
        """Put all the specified values to the cache."""
        for key, value in items:
            await self.set(key, value)

    async def delete(self, key: str) -> bool:  # pragma: no cover
        """
        Delete the key from the cache.

        Returns:
            `True` if the key has existed, `False` otherwise.
        """
        raise NotImplementedError

    async def delete_many(self, *keys: str) -> None:
        """Delete many keys at once."""

    async def clear(self) -> None:  # pragma: no cover
        """Clear the backend storage."""
        raise NotImplementedError


class AsyncBackend(
    AbstractContextManager,  # type: ignore[type-arg]
    AbstractAsyncContextManager,  # type: ignore[type-arg]
    AsyncBackendRead[WireT],
    AsyncBackendWrite[WireT],
    Generic[WireT],
    metaclass=ABCMeta,
):
    """Generic asynchronous cache backend."""

    @classmethod
    @abstractmethod
    def from_url(cls, url: str) -> AsyncBackend[Any]:  # pragma: no cover
        """
        Create an asynchronous cache backend from the specified URL.

        Returns:
            An instance of the specific backend class.
        """
        raise NotImplementedError

    def __enter__(self) -> Never:
        raise RuntimeError("use async context manager protocol instead")

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Never:
        raise RuntimeError("use async context manager protocol instead")

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None
