from __future__ import annotations

from typing import TypeVar

from typing_extensions import Protocol

from cachetory.interfaces.backends.private import WireT, WireT_co, WireT_contra

ValueT_co = TypeVar("ValueT_co", covariant=True)
"""
Value type returned by a deserializer, should be covariant so that
for A > B we could pass `Deserialize[B]` in place of `Deserialize[A]`.
"""

ValueT_contra = TypeVar("ValueT_contra", contravariant=True)
"""
Value type accepted by a serializer, should be contravariant so that
for A > B we could pass `Serialize[A]` in place of `Serialize[B]`.
"""


class Serialize(Protocol[ValueT_contra, WireT_co]):
    """Defines the `serialize` conversion."""

    def serialize(self, value: ValueT_contra) -> WireT_co:  # pragma: no cover
        raise NotImplementedError


class Deserialize(Protocol[ValueT_co, WireT_contra]):
    """Defines the `deserialize` conversion."""

    def deserialize(self, data: WireT_contra) -> ValueT_co:  # pragma: no cover
        raise NotImplementedError


ValueT = TypeVar("ValueT")
"""
Cached value type – this what user «sees» when getting or setting a value in a cache.
"""


class Serializer(Serialize[ValueT, WireT], Deserialize[ValueT, WireT], Protocol[ValueT, WireT]):
    """Combines `serialize` and `deserialize` in one protocol."""

    @classmethod
    def from_url(cls, url: str) -> Serializer[ValueT, WireT]:  # pragma: no cover
        """
        Instantiate a serializer from the specified URL.

        Returns:
            An instance of specific serializer class.
        """
        raise NotImplementedError
