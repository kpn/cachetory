from contextlib import AbstractContextManager
from datetime import timedelta
from typing import Dict, Generic, Iterable, Mapping, Optional, Tuple, Union

from cachetory.caches.private import T_default
from cachetory.interfaces.backends.private import T_wire
from cachetory.interfaces.backends.sync import SyncBackend
from cachetory.interfaces.serializers import Serializer, T_value


class Cache(Generic[T_value], AbstractContextManager):
    __slots__ = ("_serializer", "_backend")

    def __init__(self, *, serializer: Serializer[T_value, T_wire], backend: SyncBackend[T_wire]):
        self._serializer = serializer
        self._backend = backend

    def __getitem__(self, key: str) -> T_value:
        return self._serializer.deserialize(self._backend.get(key))

    def get(self, key: str, default: T_default = None) -> Union[T_value, T_default]:  # type: ignore
        try:
            return self[key]
        except KeyError:
            return default

    def get_many(self, *keys: str) -> Dict[str, T_value]:
        return {key: self._serializer.deserialize(data) for key, data in self._backend.get_many(*keys)}

    def expire_in(self, key: str, time_to_live: Optional[timedelta] = None) -> None:
        return self._backend.expire_in(key, time_to_live)

    def __setitem__(self, key: str, value: T_value) -> None:
        self._backend.set(key, self._serializer.serialize(value), time_to_live=None)

    def set(
        self,
        key: str,
        value: T_value,
        time_to_live: Optional[timedelta] = None,
        if_not_exists: bool = False,
    ) -> None:
        self._backend.set(
            key,
            self._serializer.serialize(value),
            time_to_live=time_to_live,
            if_not_exists=if_not_exists,
        )

    def set_many(self, items: Union[Iterable[Tuple[str, T_value]], Mapping[str, T_value]]) -> None:
        if isinstance(items, Mapping):
            items = items.items()
        self._backend.set_many((key, self._serializer.serialize(value)) for key, value in items)

    def delete(self, key: str) -> bool:
        return self._backend.delete(key)

    def __delitem__(self, key: str) -> None:
        self._backend.delete(key)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        return self._backend.__exit__(exc_type, exc_val, exc_tb)
