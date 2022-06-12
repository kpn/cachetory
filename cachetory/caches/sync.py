from contextlib import AbstractContextManager
from datetime import timedelta
from typing import Dict, Generic, Iterable, Mapping, Optional, Tuple, Union

from cachetory.caches.private import DefaultT
from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.backends.sync import SyncBackend
from cachetory.interfaces.serializers import Serializer, ValueT


class Cache(AbstractContextManager, Generic[ValueT]):
    """
    Synchronous cache.
    """

    __slots__ = ("_serializer", "_backend")

    def __init__(self, *, serializer: Serializer[ValueT, WireT], backend: SyncBackend[WireT]):
        self._serializer = serializer
        self._backend = backend

    def __getitem__(self, key: str) -> ValueT:
        """
        Retrieve a single value from the cache.

        Raises:
            KeyError: the key is not found in the cache
        """
        return self._serializer.deserialize(self._backend.get(key))

    def get(self, key: str, default: DefaultT = None) -> Union[ValueT, DefaultT]:  # type: ignore
        """
        Retrieve a single value from the cache.

        Args:
            key: cache key
            default: default value – if the key is not found

        Returns:
            Retrieved value if present, or `default` otherwise.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def get_many(self, *keys: str) -> Dict[str, ValueT]:
        """
        Retrieve many values from the cache.

        Returns:
            Dictionary of existing values indexed by their respective keys.
            Missing keys are omitted.
        """
        return {key: self._serializer.deserialize(data) for key, data in self._backend.get_many(*keys)}

    def expire_in(self, key: str, time_to_live: Optional[timedelta] = None) -> None:
        return self._backend.expire_in(key, time_to_live)

    def __setitem__(self, key: str, value: ValueT) -> None:
        self._backend.set(key, self._serializer.serialize(value), time_to_live=None)

    def set(
        self,
        key: str,
        value: ValueT,
        time_to_live: Optional[timedelta] = None,
        if_not_exists: bool = False,
    ) -> None:
        self._backend.set(
            key,
            self._serializer.serialize(value),
            time_to_live=time_to_live,
            if_not_exists=if_not_exists,
        )

    def set_many(self, items: Union[Iterable[Tuple[str, ValueT]], Mapping[str, ValueT]]) -> None:
        if isinstance(items, Mapping):
            items = items.items()
        self._backend.set_many((key, self._serializer.serialize(value)) for key, value in items)

    def delete(self, key: str) -> bool:
        return self._backend.delete(key)

    def __delitem__(self, key: str) -> None:
        self._backend.delete(key)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        return self._backend.__exit__(exc_type, exc_val, exc_tb)
