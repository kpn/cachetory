"""
Sync cache backend protocol descriptors.

Note, that some methods provide reasonable default implementation,
but implementors SHOULD override them for the sake of performance.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections.abc import Iterable
from contextlib import AbstractContextManager
from datetime import datetime, timedelta
from types import TracebackType
from typing import Generic

from typing_extensions import Protocol

from cachetory.interfaces.backends.private import WireT, WireT_co, WireT_contra
from cachetory.private.datetime import make_deadline


class SyncBackendRead(Protocol[WireT_co]):
    """Describes the read operations of a synchronous cache."""

    def get(self, key: str) -> WireT_co:  # pragma: no cover
        """
        Retrieve a value from the cache.

        Returns:
            Cached value, if it exists.

        Raises:
            KeyError: the key does not exist.
        """
        raise NotImplementedError

    def get_many(self, *keys: str) -> Iterable[tuple[str, WireT_co]]:
        """
        Get all the values corresponding to the specified keys.

        Returns:
            Existing key-value pairs.
        """
        for key in keys:
            try:
                value = self.get(key)
            except KeyError:
                pass
            else:
                yield key, value


class SyncBackendWrite(Protocol[WireT_contra]):
    """Describes the write operations of a synchronous cache."""

    def expire_in(self, key: str, time_to_live: timedelta | None = None) -> None:
        """Set the expiration time on the key."""
        self.expire_at(key, make_deadline(time_to_live))

    def expire_at(self, key: str, deadline: datetime | None) -> None:  # pragma: no cover
        """Set the expiration deadline on the key."""
        raise NotImplementedError

    def set(  # noqa: A003
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

    def set_many(self, items: Iterable[tuple[str, WireT_contra]]) -> None:
        """Put all the specified values to the cache."""
        for key, value in items:
            self.set(key, value)

    def delete(self, key: str) -> bool:  # pragma: no cover
        """
        Delete the key from the cache.

        Returns:
            `True` if the key has existed, `False` otherwise.
        """
        raise NotImplementedError

    def delete_many(self, *keys: str) -> None:
        """Delete many keys at once."""

    def clear(self) -> None:  # pragma: no cover
        """Clear the backend storage."""
        raise NotImplementedError


class SyncBackend(
    AbstractContextManager,  # type: ignore[type-arg]
    SyncBackendRead[WireT],
    SyncBackendWrite[WireT],
    Generic[WireT],
    metaclass=ABCMeta,
):
    """Generic synchronous cache backend."""

    @classmethod
    @abstractmethod
    def from_url(cls, url: str) -> SyncBackend[WireT]:  # pragma: no cover
        """
        Create a synchronous cache backend from the specified URL.

        Returns:
            An instance of the specific backend class.
        """
        raise NotImplementedError

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None
