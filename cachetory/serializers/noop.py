from __future__ import annotations

from typing import Generic

from cachetory.interfaces.serializers import Serializer, T_value


class NoopSerializer(Serializer[T_value, T_value], Generic[T_value]):
    """
    No-operation serializer: just forwards the value to and from backend.
    """

    @classmethod
    def from_url(cls, url: str) -> NoopSerializer[T_value]:
        return NoopSerializer[T_value]()

    def serialize(self, value: T_value) -> T_value:
        return value

    def deserialize(self, data: T_value) -> T_value:
        return data
