import pytest

try:
    # noinspection PyUnresolvedReferences
    from cachetory.serializers.msgpack import MsgPackSerializer
except ImportError:
    _is_msgpack_available = False
else:
    _is_msgpack_available = True


@pytest.mark.skipif(not _is_msgpack_available, reason="MessagePack is not available")
def test_serialize_deserialize():
    serializer = MsgPackSerializer[bytes]()
    value = b"hello, world!"
    assert serializer.deserialize(serializer.serialize(value)) == value
