from cachetory.serializers.json import JsonSerializer


def test_serialize_deserialize():
    serializer = JsonSerializer[str]()
    value = "hello, world!"
    assert serializer.deserialize(serializer.serialize(value)) == value
