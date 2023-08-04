from __future__ import annotations

from typing import Generic

import ormsgpack  # type: ignore[import]

from cachetory.interfaces.serializers import Serializer, ValueT


class MsgPackSerializer(Serializer[ValueT, bytes], Generic[ValueT]):
    """
    Uses [MessagePack](https://msgpack.org/) serialization.

    Warning:
        This serializer requires [`ormsgpack`](https://github.com/aviramha/ormsgpack) extra.
    """

    @classmethod
    def from_url(cls, url: str) -> MsgPackSerializer[ValueT]:
        """
        Construct serializer from the URL.

        # Supported schema's

        - `msgpack://`
        """
        return MsgPackSerializer[ValueT]()

    def serialize(self, value: ValueT) -> bytes:
        return ormsgpack.packb(value)

    def deserialize(self, data: bytes) -> ValueT:
        return ormsgpack.unpackb(data)
