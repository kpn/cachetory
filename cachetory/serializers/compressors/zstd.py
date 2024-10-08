from __future__ import annotations

from typing import Annotated
from urllib.parse import parse_qsl, urlparse

import zstd  # type: ignore
from pydantic import BaseModel, Field

from cachetory.interfaces.serializers import Serializer


class ZstdCompressor(Serializer[bytes, bytes]):
    """
    Uses [Zstandard](https://facebook.github.io/zstd/) compression.

    Warning:
        This compressor requires [`zstd`](https://github.com/sergey-dryabzhinsky/python-zstd) extra.
    """

    __slots__ = ("_level", "_threads")

    @classmethod
    def from_url(cls, url: str) -> ZstdCompressor:
        """
        Construct serializer from the URL.

        # Supported schema's

        - `zstd://`
        - `zstandard://`

        # URL parameters

        | Parameter             |                                                                             |
        |-----------------------|-----------------------------------------------------------------------------|
        | `compression-level`   | [Compression level](https://github.com/sergey-dryabzhinsky/python-zstd#api) |
        | `compression-threads` | [Number of threads](https://github.com/sergey-dryabzhinsky/python-zstd#api) |
        """
        params = _UrlParams.model_validate(dict(parse_qsl(urlparse(url).query)))
        return cls(compression_level=params.compression_level, compression_threads=params.compression_threads)

    def __init__(
        self,
        *,
        compression_level: int = 3,
        compression_threads: int = 0,
    ) -> None:
        self._level = compression_level
        self._threads = compression_threads

    def serialize(self, value: bytes) -> bytes:
        return zstd.compress(value, self._level, self._threads)  # type: ignore[no-any-return]

    def deserialize(self, data: bytes) -> bytes:
        return zstd.decompress(data)  # type: ignore[no-any-return]


class _UrlParams(BaseModel):
    compression_level: int = Field(3, alias="compression-level")
    compression_threads: Annotated[int, Field(ge=0)] = Field(0, alias="compression-threads")
