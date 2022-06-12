from __future__ import annotations

from typing import TypeVar

from typing_extensions import Protocol

from cachetory.interfaces.backends.private import WireT, WireT_co, WireT_contra

ValueT_co = TypeVar("ValueT_co", covariant=True)
ValueT_contra = TypeVar("ValueT_contra", contravariant=True)


class Serialize(Protocol[ValueT_contra, WireT_co]):
    """
    Defines the `serialize` conversion.
    """

    def serialize(self, value: ValueT_contra) -> WireT_co:
        raise NotImplementedError


class Deserialize(Protocol[ValueT_co, WireT_contra]):
    """
    Defines the `deserialize` conversion.
    """

    def deserialize(self, data: WireT_contra) -> ValueT_co:
        raise NotImplementedError


ValueT = TypeVar("ValueT")


class Serializer(Serialize[ValueT, WireT], Deserialize[ValueT, WireT], Protocol[ValueT, WireT]):
    """
    Combines `serialize` and `deserialize` in one protocol.
    """

    @classmethod
    def from_url(cls, url: str) -> Serializer[ValueT, WireT]:
        raise NotImplementedError
