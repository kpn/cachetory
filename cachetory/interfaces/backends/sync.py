"""
Sync cache backend protocol descriptors.

Note, that some methods provide reasonable default implementation,
but implementors SHOULD override them for the sake of performance.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, Optional, Tuple, TypeVar, Union

from typing_extensions import Protocol

# Value type as returned by cache read operations.
TV = TypeVar("TV")

# The contravariance ensures that given A > B: SyncBackendWrite[A] < SyncBackendWrite[B],
# meaning that user can safely pass SyncBackendWrite[A] in place of SyncBackendWrite[B].
# And this is needed because SyncBackendWrite[B] accepts B as a parameter,
# and so should SyncBackendWrite[A].
TV_contra = TypeVar("TV_contra", contravariant=True)

T_default = TypeVar("T_default")


class SyncBackendRead(Protocol[TV]):
    """
    Describes the read operations of a synchronous cache.
    """

    def __getitem__(self, key: str) -> TV:
        """
        Retrieve a value from the cache.

        Returns:
            Cached value, if it exists.
        Raises:
            KeyError: the key doesn't exist in the cache.
        """
        raise NotImplementedError

    def get(self, key: str, default: T_default = None) -> Union[TV, T_default]:  # type: ignore
        """
        Retrieve a value from the cache.

        Returns:
            Cached value or `None` if it doesn't exist.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def get_many(self, *keys: str) -> Dict[str, TV]:
        """
        Get all the values corresponding to the specified keys.

        Returns:
            Existing values indexed by their corresponding keys.
            Missing keys are omitted.
        """
        values = {}
        for key in keys:
            try:
                value = self[key]
            except KeyError:
                pass
            else:
                values[key] = value
        return values


class SyncBackendWrite(Protocol[TV_contra]):
    """
    Describes the write operations of a synchronous cache.
    """

    def expire_in(self, key: str, time_to_live: Optional[timedelta] = None) -> None:
        """
        Set the expiration time on the key.
        """
        deadline = datetime.now(timezone.utc) + time_to_live if time_to_live is not None else None
        self.expire_at(key, deadline)

    def expire_at(self, key: str, deadline: Optional[datetime]) -> None:
        """
        Set the expiration deadline on the key.
        """
        raise NotImplementedError

    def __setitem__(self, key: str, value: TV_contra) -> None:
        """
        Put the value into the cache, overwriting an existing one.
        """
        self.set(key, value, None)

    def set(self, key: str, value: TV_contra, time_to_live: Optional[timedelta] = None) -> None:
        """
        Put the value into the cache, overwriting an existing one.
        """
        raise NotImplementedError

    def set_many(
        self,
        items: Union[Iterable[Tuple[str, TV_contra]]],
        time_to_live: Optional[timedelta] = None,
    ) -> None:
        """
        Put all the specified values to the cache.
        """
        for (key, value) in items:
            self.set(key, value, time_to_live)

    def delete(self, key: str) -> bool:
        """
        Delete the key from the cache.

        Returns:
            `True` if the key has existed, `False` otherwise.
        """
        try:
            del self[key]
        except KeyError:
            return False
        else:
            return True

    def __delitem__(self, key: str) -> None:
        """
        Delete the key from the cache.

        Raises:
            KeyError: the key doesn't exist.
        """
        raise NotImplementedError


class SyncBackend(SyncBackendRead[TV], SyncBackendWrite[TV], Protocol[TV]):
    """
    Generic synchronous cache backend.
    This is a shorthand to combine the read and write operations.
    At the time of writing there seemed no way to please `mypy`
    while defining all the operations in a single protocol class.
    """
