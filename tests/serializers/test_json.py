from cachetory.serializers.json import JsonSerializer


def test_serialize_deserialize() -> None:
    serializer = JsonSerializer[str]()
    value = "hello, world!"
    assert serializer.deserialize(serializer.serialize(value)) == value
