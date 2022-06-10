from typing import Generic

import zstd  # type: ignore

from cachetory.interfaces.serializers import Serializer, T_value


class ZstdCompressor(Generic[T_value], Serializer[T_value, bytes]):
    """
    Wraps inner serializer with Zstandard compression.
    """

    __slots__ = ("inner", "level", "threads")

    def __init__(self, inner: Serializer[T_value, bytes], *, level: int = 3, threads: int = 0):
        self._inner = inner
        self._level = level
        self._threads = threads

    def serialize(self, value: T_value) -> bytes:
        data = self._inner.serialize(value)
        return zstd.compress(data, self._level, self._threads)

    def deserialize(self, data: bytes) -> T_value:
        data = zstd.decompress(data)
        return self._inner.deserialize(data)
