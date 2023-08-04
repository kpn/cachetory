from __future__ import annotations

import zlib
from urllib.parse import parse_qsl, urlparse

from pydantic import BaseModel, Field, conint

from cachetory.interfaces.serializers import Serializer


class ZlibCompressor(Serializer[bytes, bytes]):
    """Uses the built-in [zlib](https://docs.python.org/3/library/zlib.html) compression."""

    __slots__ = ("_level",)

    @classmethod
    def from_url(cls, url: str) -> ZlibCompressor:
        """
        Construct serializer from the URL.

        # Supported schema's

        - `zlib://`

        # URL parameters

        | Parameter           |                                                                 |
        |---------------------|-----------------------------------------------------------------|
        | `compression-level` | From `0` (no compression) to `9` (slowest and best compression) |
        """
        params = _UrlParams.parse_obj(dict(parse_qsl(urlparse(url).query)))
        return cls(compression_level=params.compression_level)

    def __init__(self, *, compression_level: int = zlib.Z_DEFAULT_COMPRESSION) -> None:
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
