from __future__ import annotations

import json
from typing import Generic

from cachetory.interfaces.serializers import Serializer, ValueT


class JsonSerializer(Serializer[ValueT, str], Generic[ValueT]):
    """Uses the standard built-in `json` serialization."""

    @classmethod
    def from_url(cls, url: str) -> JsonSerializer[ValueT]:
        return JsonSerializer[ValueT]()

    def serialize(self, value: ValueT) -> str:
        return json.dumps(value)

    def deserialize(self, data: str) -> ValueT:
        return json.loads(data)
