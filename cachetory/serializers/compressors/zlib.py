from __future__ import annotations

import zlib
from urllib.parse import parse_qsl, urlparse

from pydantic import BaseModel, Field, conint

from cachetory.interfaces.serializers import Serializer


class ZlibCompressor(Serializer[bytes, bytes]):
    """
    Uses the built-in zlib compression.
    """

    __slots__ = ("_level",)

    @classmethod
    def from_url(cls, url: str) -> ZlibCompressor:
        params = _UrlParams.parse_obj(dict(parse_qsl(urlparse(url).query)))
        return cls(compression_level=params.compression_level)

    def __init__(self, *, compression_level: int = zlib.Z_DEFAULT_COMPRESSION):
        self._level = compression_level

    def serialize(self, value: bytes) -> bytes:
        return zlib.compress(value, level=self._level)

    def deserialize(self, data: bytes) -> bytes:
        return zlib.decompress(data)


class _UrlParams(BaseModel):
    compression_level: conint(ge=-1, le=9) = Field(  # type: ignore
        zlib.Z_DEFAULT_COMPRESSION,
        alias="compression-level",
    )
