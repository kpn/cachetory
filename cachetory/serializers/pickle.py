from __future__ import annotations

import pickle
from typing import Generic

from cachetory.interfaces.serializers import Serializer, T_value


class PickleSerializer(Generic[T_value], Serializer[T_value, bytes]):
    __slots__ = ("protocol",)

    @classmethod
    def from_url(cls, url: str) -> PickleSerializer[T_value]:
        return PickleSerializer()

    def __init__(self, protocol: int = pickle.HIGHEST_PROTOCOL):
        self.protocol = protocol

    def serialize(self, value: T_value) -> bytes:
        return pickle.dumps(value, self.protocol)

    def deserialize(self, data: bytes) -> T_value:
        return pickle.loads(data)
