from cachetory.serializers import NoopSerializer
from cachetory.serializers.compressors import ZstdCompressor


def test_serialize_deserialize():
    serializer = ZstdCompressor(NoopSerializer)
    value = b"hello, world!"
    assert serializer.deserialize(serializer.serialize(value)) == value
