from typing import Generic, TypeVar

from cachetory.interfaces.serializers import Deserializer, Serializer

T_value = TypeVar("T_value")


class NoopSerializer(Generic[T_value], Serializer[T_value, T_value], Deserializer[T_value, T_value]):
    """
    No-operation serializer: just forwards the value to and from backend.
    """

    def serialize(self, value: T_value) -> T_value:
        return value

    def deserialize(self, data: T_value) -> T_value:
        return data
