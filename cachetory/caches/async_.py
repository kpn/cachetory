from __future__ import annotations

from asyncio import get_running_loop
from collections.abc import Iterable, Mapping
from concurrent.futures import Executor
from contextlib import AbstractAsyncContextManager
from datetime import timedelta
from types import TracebackType
from typing import Generic

from cachetory.caches.private import DefaultT
from cachetory.interfaces.backends.async_ import AsyncBackend
from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.serializers import Serializer, ValueT
from cachetory.private.typing import NotSet


class Cache(
    AbstractAsyncContextManager,  # type: ignore[type-arg]
    Generic[ValueT, WireT],
):
    """Asynchronous cache."""

    __slots__ = ("_serializer", "_backend", "_serialize_executor", "_prefix")

    def __init__(
        self,
        *,
        serializer: Serializer[ValueT, WireT],
        backend: AsyncBackend[WireT],
        serialize_executor: Executor | NotSet | None = NotSet(),  # noqa: B008
        prefix: str = "",
    ) -> None:
        """
        Instantiate a cache.

        Args:
            serialize_executor:
                If specified, underlying serializing and deserializing will be performed
                using the executor (for example, `ProcessPoolExecutor`).
                This may be useful to better utilize CPU when caching large blobs.
                If not specified, (de)serialization is performed in the current thread.
            prefix: backend key prefix
        """
        self._serializer = serializer
        self._backend = backend
        self._serialize_executor = serialize_executor
        self._prefix = prefix

    async def get(self, key: str, default: DefaultT = None) -> ValueT | DefaultT:  # type: ignore
        """
        Retrieve a single value from the cache.

        Args:
            key: cache key
            default: default value – if the key is not found

        Returns:
            Retrieved value if present, or `default` otherwise.

        Examples:
            >>> await cache.set("key", 42)
            >>> assert await cache.get("key") == 42
            >>> assert await cache.get("missing") is None
        """
        try:
            data = await self._backend.get(f"{self._prefix}{key}")
        except KeyError:
            return default
        else:
            return await self._deserialize(data)

    async def get_many(self, *keys: str) -> dict[str, ValueT]:
        """
        Retrieve many values from the cache.

        Returns:
            Dictionary of existing values indexed by their respective keys. Missing keys are omitted.

        Examples:
            >>> await memory_cache.set("foo", 42)
            >>> assert await memory_cache.get_many("foo", "bar") == {"foo": 42}
        """
        return {
            f"{self._prefix}{key}": await self._deserialize(data) async for key, data in self._backend.get_many(*keys)
        }

    async def expire_in(self, key: str, time_to_live: timedelta | None = None) -> None:
        """
        Set the expiration time for the key.

        Args:
            key: cache key
            time_to_live: time to live, or `None` to make it eternal
        """
        return await self._backend.expire_in(f"{self._prefix}{key}", time_to_live)

    async def set(  # noqa: A003
        self,
        key: str,
        value: ValueT,
        time_to_live: timedelta | None = None,
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
        await self._backend.set(
            f"{self._prefix}{key}",
            await self._serialize(value),
            time_to_live=time_to_live,
            if_not_exists=if_not_exists,
        )

    async def set_many(self, items: Iterable[tuple[str, ValueT]] | Mapping[str, ValueT]) -> None:
        """
        Set many cache items at once.

        Examples:
            >>> await cache.set_many({"foo": 42, "bar": 100500})
        """
        if isinstance(items, Mapping):
            items = items.items()
        await self._backend.set_many([(f"{self._prefix}{key}", await self._serialize(value)) for key, value in items])

    async def delete(self, key: str) -> bool:
        """
        Delete the cache item.

        Returns:
            `True` if the key has existed, `False` otherwise
        """
        return await self._backend.delete(f"{self._prefix}{key}")

    async def delete_many(self, *keys: str) -> None:
        """Delete many items at once."""
        await self._backend.delete_many(*(f"{self._prefix}{key}" for key in keys))

    async def clear(self) -> None:
        """Delete all cache items."""
        return await self._backend.clear()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return await self._backend.__aexit__(exc_type, exc_value, traceback)

    async def _serialize(self, value: ValueT) -> WireT:
        if isinstance(self._serialize_executor, NotSet):
            return self._serializer.serialize(value)
        else:
            return await get_running_loop().run_in_executor(self._serialize_executor, self._serializer.serialize, value)

    async def _deserialize(self, data: WireT) -> ValueT:
        if isinstance(self._serialize_executor, NotSet):
            return self._serializer.deserialize(data)
        else:
            return await get_running_loop().run_in_executor(
                self._serialize_executor,
                self._serializer.deserialize,
                data,
            )
