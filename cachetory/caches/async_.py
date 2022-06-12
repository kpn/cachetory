from contextlib import AbstractAsyncContextManager
from datetime import timedelta
from typing import Dict, Generic, Iterable, Mapping, Optional, Tuple, Union

from cachetory.caches.private import T_default
from cachetory.interfaces.backends.async_ import AsyncBackend
from cachetory.interfaces.backends.private import T_wire
from cachetory.interfaces.serializers import Serializer, T_value


class Cache(Generic[T_value], AbstractAsyncContextManager):
    __slots__ = ("_serializer", "_backend")

    def __init__(self, *, serializer: Serializer[T_value, T_wire], backend: AsyncBackend[T_wire]):
        self._serializer = serializer
        self._backend = backend

    async def get(self, key: str, default: T_default = None) -> Union[T_value, T_default]:  # type: ignore
        try:
            data = await self._backend.get(key)
        except KeyError:
            return default
        else:
            return self._serializer.deserialize(data)

    async def get_many(self, *keys: str) -> Dict[str, T_value]:
        return {key: self._serializer.deserialize(data) async for key, data in self._backend.get_many(*keys)}

    async def expire_in(self, key: str, time_to_live: Optional[timedelta] = None) -> None:
        return await self._backend.expire_in(key, time_to_live)

    async def set(
        self,
        key: str,
        value: T_value,
        time_to_live: Optional[timedelta] = None,
        if_not_exists: bool = False,
    ) -> None:
        await self._backend.set(
            key,
            self._serializer.serialize(value),
            time_to_live=time_to_live,
            if_not_exists=if_not_exists,
        )

    async def set_many(self, items: Union[Iterable[Tuple[str, T_value]], Mapping[str, T_value]]) -> None:
        if isinstance(items, Mapping):
            items = items.items()
        await self._backend.set_many((key, self._serializer.serialize(value)) for key, value in items)

    async def delete(self, key: str) -> bool:
        return await self._backend.delete(key)

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        return await self._backend.__aexit__(exc_type, exc_val, exc_tb)
