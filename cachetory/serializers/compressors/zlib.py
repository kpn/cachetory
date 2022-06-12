from __future__ import annotations

import zlib
from contextlib import suppress
from urllib.parse import parse_qs, urlparse

from cachetory.interfaces.serializers import Serializer


class ZlibCompressor(Serializer[bytes, bytes]):
    """
    Uses the built-in zlib compression.
    """

    __slots__ = ("_level",)

    @classmethod
    def from_url(cls, url: str) -> ZlibCompressor:
        params = parse_qs(urlparse(url).query)
        parsed_params = {}
        with suppress(KeyError, IndexError):
            parsed_params["compression_level"] = int(params["compression-level"][0])
        return cls(**parsed_params)

    def __init__(self, *, compression_level: int = zlib.Z_DEFAULT_COMPRESSION):
        self._level = compression_level

    def serialize(self, value: bytes) -> bytes:
        return zlib.compress(value, level=self._level)

    def deserialize(self, data: bytes) -> bytes:
        return zlib.decompress(data)
