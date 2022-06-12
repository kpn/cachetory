from __future__ import annotations

from typing import Generic

from cachetory.interfaces.serializers import Serializer, ValueT


class NoopSerializer(Serializer[ValueT, ValueT], Generic[ValueT]):
    """
    No-operation serializer: just forwards the value to and from backend.
    """

    @classmethod
    def from_url(cls, url: str) -> NoopSerializer[ValueT]:
        return NoopSerializer[ValueT]()

    def serialize(self, value: ValueT) -> ValueT:
        return value

    def deserialize(self, data: ValueT) -> ValueT:
        return data
