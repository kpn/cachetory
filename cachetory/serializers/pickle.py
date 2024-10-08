from __future__ import annotations

import pickle
from typing import Annotated, Generic
from urllib.parse import parse_qsl, urlparse

from pydantic import BaseModel, Field

from cachetory.interfaces.serializers import Serializer, ValueT


class PickleSerializer(Serializer[ValueT, bytes], Generic[ValueT]):
    """
    Uses the standard built-in [`pickle`][1] serialization.

    [1]: https://docs.python.org/3/library/pickle.html
    """

    __slots__ = ("protocol",)

    @classmethod
    def from_url(cls, url: str) -> PickleSerializer[ValueT]:
        """
        Construct serializer from the URL.

        # Supported schema's

        - `pickle://`

        # URL parameters

        | Parameter         |                           |
        |-------------------|---------------------------|
        | `pickle-protocol` | `pickle` protocol version |
        """
        params = _UrlParams.model_validate(dict(parse_qsl(urlparse(url).query)))
        return cls(pickle_protocol=params.pickle_protocol)

    def __init__(self, pickle_protocol: int = pickle.HIGHEST_PROTOCOL) -> None:
        """
        Initialize the serializer.

        Args:
            pickle_protocol: `pickle` protocol version
        """
        self.protocol = pickle_protocol

    def serialize(self, value: ValueT) -> bytes:
        return pickle.dumps(value, self.protocol)

    def deserialize(self, data: bytes) -> ValueT:
        return pickle.loads(data)  # type: ignore[no-any-return]


class _UrlParams(BaseModel):
    pickle_protocol: Annotated[int, Field(ge=0, le=pickle.HIGHEST_PROTOCOL)] = Field(
        pickle.HIGHEST_PROTOCOL,
        alias="pickle-protocol",
    )
