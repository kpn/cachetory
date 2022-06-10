"""
Sync cache backend protocol descriptors.

Note, that some methods provide reasonable default implementation,
but implementors SHOULD override them for the sake of performance.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, Optional, Tuple

from typing_extensions import Protocol

from cachetory.interfaces.backends.shared import T_wire, T_wire_contra, T_wire_cov
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
        entries = []
        for key in keys:
            try:
                value = self.get(key)
            except KeyError:
                pass
            else:
                entries.append((key, value))
        return entries


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
    ) -> None:
        """
        Put the value into the cache, overwriting an existing one.
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


class SyncBackend(SyncBackendRead[T_wire], SyncBackendWrite[T_wire], Protocol[T_wire]):
    """
    Generic synchronous cache backend.
    This is a shorthand to combine the read and write operations.
    At the time of writing there seemed no way to please `mypy`
    while defining all the operations in a single protocol class.
    """
