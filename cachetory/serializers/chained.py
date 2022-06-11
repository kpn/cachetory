from __future__ import annotations

from typing import Any, Generic, Iterable, cast
from urllib.parse import urlparse

from cachetory.interfaces.backends.private import T_wire
from cachetory.interfaces.serializers import Serializer, T_value
from cachetory.serializers.compressors.zlib import ZlibCompressor
from cachetory.serializers.noop import NoopSerializer
from cachetory.serializers.pickle import PickleSerializer

try:
    # noinspection PyUnresolvedReferences
    from cachetory.serializers.compressors import ZstdCompressor
except ImportError:
    is_zstd_available = False
else:
    is_zstd_available = True


class ChainedSerializer(Generic[T_value, T_wire], Serializer[T_value, T_wire]):
    """
    Sequentially applies the chain of serializers.
    """

    __slots__ = ("_layers",)

    @classmethod
    def from_url(cls, url: str) -> ChainedSerializer[T_value, T_wire]:
        parsed_url = urlparse(url)
        schemes = parsed_url.scheme.split("+")
        return cls(cls._make_layer(scheme, url) for scheme in schemes)

    def __init__(self, layers: Iterable[Serializer]):
        self._layers = list(layers)

    def serialize(self, value: T_value) -> T_wire:
        value = cast(Any, value)
        for layer in self._layers:
            value = layer.serialize(value)
        return cast(T_wire, value)

    def deserialize(self, data: T_wire) -> T_value:
        value = cast(Any, data)
        for layer in self._layers[::-1]:
            value = layer.deserialize(value)
        return cast(T_value, value)

    @classmethod
    def _make_layer(cls, scheme: str, url: str) -> Serializer:
        if scheme == "pickle":
            return PickleSerializer.from_url(url)
        if scheme in ("noop", "null"):
            return NoopSerializer.from_url(url)
        if scheme == "zstd" and is_zstd_available:
            return ZstdCompressor.from_url(url)
        if scheme == "zlib":
            return ZlibCompressor.from_url(url)
        raise ValueError(f"`{scheme}://` is not supported")
