from typing import List, Type

from pytest import mark, raises

from cachetory.interfaces.serializers import Serializer
from cachetory.serializers import ChainedSerializer, PickleSerializer
from cachetory.serializers.compressors import ZstdCompressor


@mark.parametrize(
    "url, expected_layers",
    [
        ("pickle://", [PickleSerializer]),
        ("pickle+zstd://", [PickleSerializer, ZstdCompressor]),
    ],
)
def test_layers(url: str, expected_layers: List[Type[Serializer]]):
    assert [type(layer) for layer in ChainedSerializer.from_url(url)._layers] == expected_layers


def test_unsupported_scheme():
    with raises(ValueError):
        ChainedSerializer.from_url("subspace://")


def test_serialize():
    serializer: Serializer[str, bytes] = ChainedSerializer.from_url("pickle+zstd://")
    value = "Shields up! Red alert!"
    assert serializer.serialize(value) == ZstdCompressor().serialize(PickleSerializer().serialize(value))


def test_deserialize():
    value = "Energize!"
    serialized_value = ZstdCompressor().serialize(PickleSerializer().serialize(value))
    assert ChainedSerializer.from_url("pickle+zstd://").deserialize(serialized_value) == value
