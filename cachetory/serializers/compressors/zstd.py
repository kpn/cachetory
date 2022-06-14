from __future__ import annotations

from urllib.parse import parse_qsl, urlparse

import zstd  # type: ignore
from pydantic import BaseModel, Field, conint

from cachetory.interfaces.serializers import Serializer


class ZstdCompressor(Serializer[bytes, bytes]):
    """
    Uses external `zstd` package for Zstandard compression.
    """

    __slots__ = ("_level", "_threads")

    @classmethod
    def from_url(cls, url: str) -> ZstdCompressor:
        params = _UrlParams.parse_obj(dict(parse_qsl(urlparse(url).query)))
        return cls(compression_level=params.compression_level, compression_threads=params.compression_threads)

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


class _UrlParams(BaseModel):
    compression_level: int = Field(3, alias="compression-level")  # type: ignore
    compression_threads: conint(ge=0) = Field(0, alias="compression-threads")  # type: ignore
