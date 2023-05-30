from __future__ import annotations

from typing import Generic

import ormsgpack  # type: ignore[import]

from cachetory.interfaces.serializers import Serializer, ValueT


class MsgPackSerializer(Serializer[ValueT, bytes], Generic[ValueT]):
    """Uses the non-standard built-in `msgpack` serialization."""

    @classmethod
    def from_url(cls, url: str) -> MsgPackSerializer[ValueT]:
        return MsgPackSerializer[ValueT]()

    def serialize(self, value: ValueT) -> bytes:
        return ormsgpack.packb(value)

    def deserialize(self, data: bytes) -> ValueT:
        return ormsgpack.unpackb(data)
