from cachetory.serializers.compressors.zstd import ZstdCompressor


def test_serialize_deserialize():
    serializer = ZstdCompressor()
    value = b"hello, world!"
    assert serializer.deserialize(serializer.serialize(value)) == value
