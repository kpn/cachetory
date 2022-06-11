from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import zstd  # type: ignore

from cachetory.interfaces.serializers import Serializer


class ZstdCompressor(Serializer[bytes, bytes]):
    """
    Compresses and decompresses a byte array into a byte array.
    """

    __slots__ = ("level", "threads")

    @classmethod
    def from_url(cls, url: str) -> ZstdCompressor:
        parsed_url = urlparse(url)
        params = parse_qs(parsed_url.query)

        try:
            compression_level = int(params["compression_level"][0])
        except (KeyError, IndexError):
            compression_level = 3

        return cls(compression_level=compression_level)

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
