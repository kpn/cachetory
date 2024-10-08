from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Generic, cast
from urllib.parse import urlparse

from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.serializers import Serializer, ValueT
from cachetory.serializers.compressors.zlib import ZlibCompressor
from cachetory.serializers.json import JsonSerializer
from cachetory.serializers.noop import NoopSerializer
from cachetory.serializers.pickle import PickleSerializer

try:
    # noinspection PyUnresolvedReferences
    from cachetory.serializers.compressors import ZstdCompressor
except ImportError:
    _is_zstd_available = False
else:
    _is_zstd_available = True

try:
    # noinspection PyUnresolvedReferences
    from cachetory.serializers.msgpack import MsgPackSerializer
except ImportError:
    _is_msgpack_available = False
else:
    _is_msgpack_available = True


class ChainedSerializer(Serializer[ValueT, WireT], Generic[ValueT, WireT]):
    """Sequentially applies the chain of serializers. It allows defining multiple steps of serialization."""

    __slots__ = ("_layers",)

    @classmethod
    def from_url(cls, url: str) -> ChainedSerializer[ValueT, WireT]:
        """
        Construct serializer from the URL.

        This method parses the URL and constructs serializer layers based on the schema's
        and query parameters.

        Examples:
            >>> serializer = ChainedSerializer.from_url(
            >>>     # Serialize with Pickle and then compress with Zstandard:
            >>>     "pickle+zstd://?pickle-protocol=4&compression-level=3",
            >>> )
        """
        parsed_url = urlparse(url)
        schemes = parsed_url.scheme.split("+")
        return cls(cls._make_layer(scheme, url) for scheme in schemes)

    def __init__(self, layers: Iterable[Serializer[ValueT, WireT]]) -> None:
        """
        Initialize the chained serializer.

        Args:
            layers: iterable of other serializers which are then applied sequentially
        """
        self._layers = list(layers)

    def serialize(self, value: ValueT) -> WireT:
        value_: Any = value
        for layer in self._layers:
            value_ = layer.serialize(value_)
        return cast(WireT, value_)

    def deserialize(self, data: WireT) -> ValueT:
        value: Any = data
        for layer in self._layers[::-1]:
            value = layer.deserialize(value)
        return cast(ValueT, value)

    @classmethod
    def _make_layer(cls, scheme: str, url: str) -> Serializer[Any, Any]:
        if scheme == "json":
            return JsonSerializer.from_url(url)
        if scheme == "msgpack":
            if not _is_msgpack_available:
                raise ValueError(f"`{scheme}://` requires `cachetory[msgpack]` extra")
            return MsgPackSerializer.from_url(url)
        if scheme == "pickle":
            return PickleSerializer.from_url(url)
        if scheme in ("noop", "null"):
            return NoopSerializer.from_url(url)
        if scheme in ("zstd", "zstandard"):
            if not _is_zstd_available:
                raise ValueError(f"`{scheme}://` requires `cachetory[zstd]` extra")
            return ZstdCompressor.from_url(url)
        if scheme == "zlib":
            return ZlibCompressor.from_url(url)
        raise ValueError(f"`{scheme}://` is not supported")
