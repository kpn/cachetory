from __future__ import annotations

import pickle
from contextlib import suppress
from typing import Generic
from urllib.parse import parse_qs, urlparse

from cachetory.interfaces.serializers import Serializer, T_value


class PickleSerializer(Generic[T_value], Serializer[T_value, bytes]):
    __slots__ = ("protocol",)

    @classmethod
    def from_url(cls, url: str) -> PickleSerializer[T_value]:
        params = parse_qs(urlparse(url).query)
        parsed_params = {}
        with suppress(KeyError, IndexError):
            parsed_params["pickle_protocol"] = int(params["pickle-protocol"][0])
        return cls(**parsed_params)

    def __init__(self, pickle_protocol: int = pickle.HIGHEST_PROTOCOL):
        self.protocol = pickle_protocol

    def serialize(self, value: T_value) -> bytes:
        return pickle.dumps(value, self.protocol)

    def deserialize(self, data: bytes) -> T_value:
        return pickle.loads(data)
