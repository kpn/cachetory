from typing import Generic

from cachetory.interfaces.serializers import Serializer, T_value


class NoopSerializer(Generic[T_value], Serializer[T_value, T_value]):
    """
    No-operation serializer: just forwards the value to and from backend.
    """

    @staticmethod
    def serialize(value: T_value) -> T_value:
        return value

    @staticmethod
    def deserialize(data: T_value) -> T_value:
        return data
