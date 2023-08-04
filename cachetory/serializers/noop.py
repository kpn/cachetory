from __future__ import annotations

from typing import Generic

from cachetory.interfaces.serializers import Serializer, ValueT


class NoopSerializer(Serializer[ValueT, ValueT], Generic[ValueT]):
    """
    No-operation serializer: just forwards the value to and from backend.

    Tip:
        This serializer is especially useful with the dummy or memory backend since they do not
        really need any serializer and having a one would only waste CPU cycles.
    """

    @classmethod
    def from_url(cls, url: str) -> NoopSerializer[ValueT]:
        """
        Construct serializer from the URL.

        # Supported schema's

        - `noop://`
        - `null://`
        """
        return NoopSerializer[ValueT]()

    def serialize(self, value: ValueT) -> ValueT:
        return value

    def deserialize(self, data: ValueT) -> ValueT:
        return data
