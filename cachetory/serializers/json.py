from __future__ import annotations

import json
from typing import Generic

from cachetory.interfaces.serializers import Serializer, ValueT


class JsonSerializer(Serializer[ValueT, str], Generic[ValueT]):
    """
    Uses the standard built-in [`json`][1] serialization.

    [1]: https://docs.python.org/3/library/json.html
    """

    @classmethod
    def from_url(cls, url: str) -> JsonSerializer[ValueT]:
        """
        Construct serializer from the URL.

        # Supported schema's

        - `json://`
        """
        return JsonSerializer[ValueT]()

    def serialize(self, value: ValueT) -> str:
        return json.dumps(value)

    def deserialize(self, data: str) -> ValueT:
        return json.loads(data)  # type: ignore[no-any-return]
