"""
Async cache backend protocol descriptors.

Note, that some methods provide reasonable default implementation,
but implementors SHOULD override them for the sake of performance.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Awaitable, Dict, Iterable, Optional, Tuple, Union

from typing_extensions import Protocol

from cachetory.interfaces.backends.shared import T_default, T_value, T_value_contra


class AsyncBackendRead(Protocol[T_value]):
    """
    Describes the read operations of an asynchronous cache.
    """

    def __getitem__(self, key: str) -> Awaitable[T_value]:
        """
        Retrieve a value from the cache.

        Returns:
            Awaitable of the cached value, if it exists.
        Raises:
            KeyError: the key doesn't exist in the cache.
        """
        raise NotImplementedError

    async def get(self, key: str, default: T_default = None) -> Union[T_value, T_default]:  # type: ignore
        """
        Retrieve a value from the cache.

        Returns:
            Cached value or `None` if it doesn't exist.
        """
        try:
            return await self[key]
        except KeyError:
            return default

    async def get_many(self, *keys: str) -> Dict[str, T_value]:
        """
        Get all the values corresponding to the specified keys.

        Returns:
            Existing values indexed by their corresponding keys.
            Missing keys are omitted.
        """
        values = {}
        for key in keys:
            try:
                value = await self[key]
            except KeyError:
                pass
            else:
                values[key] = value
        return values


class AsyncBackendWrite(Protocol[T_value_contra]):
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

    async def set(self, key: str, value: T_value_contra, time_to_live: Optional[timedelta] = None) -> None:
        """
        Put the value into the cache, overwriting an existing one.
        """
        raise NotImplementedError

    async def set_default(self, key: str, value: T_value_contra, time_to_live: Optional[timedelta] = None) -> None:
        """
        Put the value into the cache, only if it isn't already existing.
        """
        raise NotImplementedError

    async def set_many(
        self,
        items: Union[Iterable[Tuple[str, T_value_contra]]],
        time_to_live: Optional[timedelta] = None,
    ) -> None:
        """
        Put all the specified values to the cache.
        """
        for (key, value) in items:
            await self.set(key, value, time_to_live)

    async def delete(self, key: str) -> bool:
        """
        Delete the key from the cache.

        Returns:
            `True` if the key has existed, `False` otherwise.
        """
        raise NotImplementedError

    def __setitem__(self, _key: Any, _value: Any):
        # Can't return an awaitable from it.
        raise ValueError("this operation is not supported on an async backend")

    def __delitem__(self, _key: Any, _value: Any):
        # Can't return an awaitable from it.
        raise ValueError("this operation is not supported on an async backend")


class AsyncBackend(AsyncBackendRead[T_value], AsyncBackendWrite[T_value], Protocol[T_value]):
    """
    Generic asynchronous cache backend.
    """
