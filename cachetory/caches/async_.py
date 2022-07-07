from asyncio import get_running_loop
from concurrent.futures import Executor
from contextlib import AbstractAsyncContextManager
from datetime import timedelta
from typing import Dict, Generic, Iterable, Mapping, Optional, Tuple, Union

from cachetory.caches.private import DefaultT
from cachetory.interfaces.backends.async_ import AsyncBackend
from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.serializers import Serializer, ValueT
from cachetory.private.typing import NotSet

_NOT_SET = NotSet()


class Cache(AbstractAsyncContextManager, Generic[ValueT]):
    """
    Asynchronous cache.
    """

    __slots__ = ("_serializer", "_backend", "_serialize_executor")

    def __init__(
        self,
        *,
        serializer: Serializer[ValueT, WireT],
        backend: AsyncBackend[WireT],
        serialize_executor: Union[None, Executor, NotSet] = _NOT_SET,
    ):
        """
        Args:
            serialize_executor:
                If specified, underlying serializing and deserializing will be performed
                using the executor (for example, ``concurrent.futures.ProcessPoolExecutor``).
                This may be useful to better utilize CPU when caching large blobs.
                If not specified, (de)serialization is performed in the current thread.
        """
        self._serializer = serializer
        self._backend = backend
        self._serialize_executor = serialize_executor

    async def get(self, key: str, default: DefaultT = None) -> Union[ValueT, DefaultT]:  # type: ignore
        try:
            data = await self._backend.get(key)
        except KeyError:
            return default
        else:
            return await self._deserialize(data)

    async def get_many(self, *keys: str) -> Dict[str, ValueT]:
        return {key: await self._deserialize(data) async for key, data in self._backend.get_many(*keys)}

    async def expire_in(self, key: str, time_to_live: Optional[timedelta] = None) -> None:
        return await self._backend.expire_in(key, time_to_live)

    async def set(
        self,
        key: str,
        value: ValueT,
        time_to_live: Optional[timedelta] = None,
        if_not_exists: bool = False,
    ) -> None:
        await self._backend.set(
            key,
            await self._serialize(value),
            time_to_live=time_to_live,
            if_not_exists=if_not_exists,
        )

    async def set_many(self, items: Union[Iterable[Tuple[str, ValueT]], Mapping[str, ValueT]]) -> None:
        if isinstance(items, Mapping):
            items = items.items()
        await self._backend.set_many([(key, await self._serialize(value)) for key, value in items])

    async def delete(self, key: str) -> bool:
        return await self._backend.delete(key)

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        return await self._backend.__aexit__(exc_type, exc_val, exc_tb)

    async def _serialize(self, value: ValueT) -> WireT:
        if self._serialize_executor is _NOT_SET:
            return self._serializer.serialize(value)
        else:
            return await get_running_loop().run_in_executor(self._serialize_executor, self._serializer.serialize, value)

    async def _deserialize(self, data: WireT) -> ValueT:
        if self._serialize_executor is _NOT_SET:
            return self._serializer.deserialize(data)
        else:
            return await get_running_loop().run_in_executor(
                self._serialize_executor, self._serializer.deserialize, data
            )
