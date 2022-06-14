from __future__ import annotations

from contextlib import suppress
from urllib.parse import parse_qsl, urlparse

import zstd  # type: ignore

from cachetory.interfaces.serializers import Serializer


class ZstdCompressor(Serializer[bytes, bytes]):
    """
    Uses external `zstd` package for Zstandard compression.
    """

    __slots__ = ("_level", "_threads")

    @classmethod
    def from_url(cls, url: str) -> ZstdCompressor:
        params = dict(parse_qsl(urlparse(url).query))
        parsed_params = {}
        with suppress(KeyError, IndexError):
            parsed_params["compression_level"] = int(params["compression-level"])
        with suppress(KeyError, IndexError):
            parsed_params["compression_threads"] = int(params["compression-threads"])
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
