from __future__ import annotations

from contextlib import suppress
from urllib.parse import parse_qs, urlparse

import zstd  # type: ignore

from cachetory.interfaces.serializers import Serializer


class ZstdCompressor(Serializer[bytes, bytes]):
    __slots__ = ("_level", "_threads")

    @classmethod
    def from_url(cls, url: str) -> ZstdCompressor:
        params = parse_qs(urlparse(url).query)
        parsed_params = {}
        with suppress(KeyError, IndexError):
            parsed_params["compression_level"] = int(params["compression-level"][0])
        with suppress(KeyError, IndexError):
            parsed_params["compression_threads"] = int(params["compression-threads"][0])
        return cls(**parsed_params)

    def __init__(
        self,
        *,
        compression_level: int = 3,
        compression_threads: int = 0,
    ):
        self._level = compression_level
        self._threads = compression_threads

    def serialize(self, value: bytes) -> bytes:
        return zstd.compress(value, self._level, self._threads)

    def deserialize(self, data: bytes) -> bytes:
        return zstd.decompress(data)
