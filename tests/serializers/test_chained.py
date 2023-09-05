from typing import List, Type

import pytest
from pytest import mark, raises

from cachetory.interfaces.serializers import Serializer
from cachetory.serializers import ChainedSerializer, PickleSerializer
from cachetory.serializers.compressors import ZstdCompressor

try:
    # noinspection PyUnresolvedReferences
    from cachetory.serializers.msgpack import MsgPackSerializer
except ImportError:
    _is_msgpack_available = False
else:
    _is_msgpack_available = True


@mark.parametrize(
    ("url", "expected_layers"),
    [
        ("pickle://", [PickleSerializer]),
        ("pickle+zstd://", [PickleSerializer, ZstdCompressor]),
    ],
)
def test_layers(url: str, expected_layers: List[Type[Serializer]]) -> None:
    assert [type(layer) for layer in ChainedSerializer.from_url(url)._layers] == expected_layers


def test_unsupported_scheme() -> None:
    with raises(ValueError):
        ChainedSerializer.from_url("subspace://")


def test_serialize() -> None:
    serializer: Serializer[str, bytes] = ChainedSerializer.from_url("pickle+zstd://")
    value = "Shields up! Red alert!"
    assert serializer.serialize(value) == ZstdCompressor().serialize(PickleSerializer[str]().serialize(value))


@pytest.mark.skipif(not _is_msgpack_available, reason="MessagePack is not available")
def test_msgpack_serialize() -> None:
    serializer: Serializer[str, bytes] = ChainedSerializer.from_url("msgpack+zstd://")
    value = "Shields up! Red alert!"
    assert serializer.serialize(value) == ZstdCompressor().serialize(MsgPackSerializer[str]().serialize(value))


def test_deserialize() -> None:
    value = "Energize!"
    serialized_value = ZstdCompressor().serialize(PickleSerializer[str]().serialize(value))
    assert ChainedSerializer[str, bytes].from_url("pickle+zstd://").deserialize(serialized_value) == value


@pytest.mark.skipif(not _is_msgpack_available, reason="MessagePack is not available")
def test_msgpack_deserialize() -> None:
    value = "Energize!"
    serialized_value = ZstdCompressor().serialize(MsgPackSerializer[str]().serialize(value))
    assert ChainedSerializer[str, bytes].from_url("msgpack+zstd://").deserialize(serialized_value) == value
