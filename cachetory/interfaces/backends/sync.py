"""
Sync cache backend protocol descriptors.

Note, that some methods provide reasonable default implementation,
but implementors SHOULD override them for the sake of performance.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from contextlib import AbstractContextManager
from datetime import datetime, timedelta
from typing import Generic, Iterable, Optional, Tuple

from typing_extensions import Protocol

from cachetory.interfaces.backends.private import T_wire, T_wire_contra, T_wire_cov
from cachetory.private.datetime import make_deadline


class SyncBackendRead(Protocol[T_wire_cov]):
    """
    Describes the read operations of a synchronous cache.
    """

    def get(self, key: str) -> T_wire_cov:
        """
        Retrieve a value from the cache.

        Returns:
            Cached value, if it exists.
        Raises:
            KeyError: the key does not exist.
        """
        raise NotImplementedError

    def get_many(self, *keys: str) -> Iterable[Tuple[str, T_wire_cov]]:
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


class SyncBackendWrite(Protocol[T_wire_contra]):
    """
    Describes the write operations of a synchronous cache.
    """

    def expire_in(self, key: str, time_to_live: Optional[timedelta] = None) -> None:
        """
        Set the expiration time on the key.
        """
        self.expire_at(key, make_deadline(time_to_live))

    def expire_at(self, key: str, deadline: Optional[datetime]) -> None:
        """
        Set the expiration deadline on the key.
        """
        raise NotImplementedError

    def set(
        self,
        key: str,
        value: T_wire_contra,
        *,
        time_to_live: Optional[timedelta] = None,
        if_not_exists: bool = False,
    ) -> bool:
        """
        Put the value into the cache.

        Returns:
            `True` if the value has been successfully set, `False` when `if_not_exists` is true
            and the key is already existing.
        """
        raise NotImplementedError

    def set_many(self, items: Iterable[Tuple[str, T_wire_contra]]) -> None:
        """
        Put all the specified values to the cache.
        """
        for (key, value) in items:
            self.set(key, value)

    def delete(self, key: str) -> bool:
        """
        Delete the key from the cache.

        Returns:
            `True` if the key has existed, `False` otherwise.
        """
        raise NotImplementedError

    def clear(self) -> None:
        """
        Clears the backend storage.
        """
        raise NotImplementedError


class SyncBackend(
    AbstractContextManager,
    SyncBackendRead[T_wire],
    SyncBackendWrite[T_wire],
    Generic[T_wire],
    metaclass=ABCMeta,
):
    """
    Generic synchronous cache backend.
    """

    @classmethod
    @abstractmethod
    def from_url(cls, url: str) -> SyncBackend:
        raise NotImplementedError

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None
