from __future__ import annotations

from typing import Any, Generic, Iterable, cast
from urllib.parse import urlparse

from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.serializers import Serializer, ValueT
from cachetory.serializers.compressors.zlib import ZlibCompressor
from cachetory.serializers.noop import NoopSerializer
from cachetory.serializers.pickle import PickleSerializer

try:
    # noinspection PyUnresolvedReferences
    from cachetory.serializers.compressors import ZstdCompressor
except ImportError:
    _is_zstd_available = False
else:
    _is_zstd_available = True


class ChainedSerializer(Serializer[ValueT, WireT], Generic[ValueT, WireT]):
    """
    Sequentially applies the chain of serializers.
    Allows defining multiple steps of serialization.
    """

    __slots__ = ("_layers",)

    @classmethod
    def from_url(cls, url: str) -> ChainedSerializer[ValueT, WireT]:
        parsed_url = urlparse(url)
        schemes = parsed_url.scheme.split("+")
        return cls(cls._make_layer(scheme, url) for scheme in schemes)

    def __init__(self, layers: Iterable[Serializer]):
        self._layers = list(layers)

    def serialize(self, value: ValueT) -> WireT:
        value = cast(Any, value)
        for layer in self._layers:
            value = layer.serialize(value)
        return cast(WireT, value)

    def deserialize(self, data: WireT) -> ValueT:
        value = cast(Any, data)
        for layer in self._layers[::-1]:
            value = layer.deserialize(value)
        return cast(ValueT, value)

    @classmethod
    def _make_layer(cls, scheme: str, url: str) -> Serializer:
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
