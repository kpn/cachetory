from collections.abc import Iterable, Mapping
from contextlib import AbstractContextManager
from datetime import timedelta
from types import TracebackType
from typing import Generic, Optional, Union

from cachetory.caches.private import DefaultT
from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.backends.sync import SyncBackend
from cachetory.interfaces.serializers import Serializer, ValueT


class Cache(
    AbstractContextManager,  # type: ignore[type-arg]
    Generic[ValueT, WireT],
):
    """Synchronous cache."""

    __slots__ = ("_serializer", "_backend", "_prefix")

    def __init__(self, *, serializer: Serializer[ValueT, WireT], backend: SyncBackend[WireT], prefix: str = "") -> None:
        """
        Instantiate a cache.

        Args:
            prefix: backend key prefix
        """
        self._serializer = serializer
        self._backend = backend
        self._prefix = prefix

    def __getitem__(self, key: str) -> ValueT:
        """
        Retrieve a single value from the cache.

        Raises:
            KeyError: the key is not found in the cache

        Examples:
            >>> cache["key"] = 42
            >>>
            >>> assert cache["key"] == 42
            >>>
            >>> with pytest.raises(KeyError):
            >>>     _ = cache["missing"]
        """
        return self._serializer.deserialize(self._backend.get(f"{self._prefix}{key}"))

    def get(self, key: str, default: DefaultT = None) -> Union[ValueT, DefaultT]:  # type: ignore
        """
        Retrieve a single value from the cache.

        Args:
            key: cache key
            default: default value – if the key is not found

        Returns:
            Retrieved value if present, or `default` otherwise.

        Examples:
            >>> cache["key"] = 42
            >>> assert cache.get("key") == 42
            >>> assert cache.get("missing") is None
        """
        try:
            return self[key]
        except KeyError:
            return default

    def get_many(self, *keys: str) -> dict[str, ValueT]:
        """
        Retrieve many values from the cache.

        Returns:
            Dictionary of existing values indexed by their respective keys. Missing keys are omitted.

        Examples:
            >>> cache["key"] = 42
            >>> assert cache.get_many("key", "missing") == {"key": 42}
        """
        return {
            f"{self._prefix}{key}": self._serializer.deserialize(data) for key, data in self._backend.get_many(*keys)
        }

    def expire_in(self, key: str, time_to_live: Optional[timedelta] = None) -> None:
        """
        Set the expiration time for the key.

        Args:
            key: cache key
            time_to_live: time to live, or `None` to make it eternal
        """
        return self._backend.expire_in(f"{self._prefix}{key}", time_to_live)

    def __setitem__(self, key: str, value: ValueT) -> None:
        """Set the cache item. To customize the behavior, use `set()`."""
        self._backend.set(f"{self._prefix}{key}", self._serializer.serialize(value), time_to_live=None)

    def set(  # noqa: A003
        self,
        key: str,
        value: ValueT,
        time_to_live: Optional[timedelta] = None,
        if_not_exists: bool = False,
    ) -> None:
        """
        Set the cache item.

        Args:
            key: cache key
            value: cached value
            time_to_live: time to live, or `None` for eternal caching
            if_not_exists: only set the item if it does not already exist
        """
        self._backend.set(
            f"{self._prefix}{key}",
            self._serializer.serialize(value),
            time_to_live=time_to_live,
            if_not_exists=if_not_exists,
        )

    def set_many(self, items: Union[Iterable[tuple[str, ValueT]], Mapping[str, ValueT]]) -> None:
        """
        Set many cache items at once.

        Examples:
            >>> cache.set_many({"foo": 42, "bar": 100500})
        """
        if isinstance(items, Mapping):
            items = items.items()
        self._backend.set_many((f"{self._prefix}{key}", self._serializer.serialize(value)) for key, value in items)

    def delete(self, key: str) -> bool:
        """
        Delete the cache item.

        Returns:
            `True` if the key has existed, `False` otherwise
        """
        return self._backend.delete(f"{self._prefix}{key}")

    def delete_many(self, *keys: str) -> None:
        """Delete many items at once."""
        self._backend.delete_many(*(f"{self._prefix}{key}" for key in keys))

    def clear(self) -> None:
        """Delete all cache items."""
        return self._backend.clear()

    def __delitem__(self, key: str) -> None:
        """
        Delete the cache item.

        Raises:
            KeyError: the key didn't exist
        """
        if not self.delete(key):
            raise KeyError(key)

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        return self._backend.__exit__(exc_type, exc_val, exc_tb)
