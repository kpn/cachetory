from typing import TypeVar

from typing_extensions import Protocol

from cachetory.interfaces.backends.shared import T_wire

T_value_cov = TypeVar("T_value_cov", covariant=True)
T_value_contra = TypeVar("T_value_contra", contravariant=True)

T_wire_cov = TypeVar("T_wire_cov", covariant=True)
T_wire_contra = TypeVar("T_wire_contra", contravariant=True)


class Serialize(Protocol[T_value_contra, T_wire_cov]):
    """
    Defines the `serialize` conversion.
    """

    def serialize(self, value: T_value_contra) -> T_wire_cov:
        raise NotImplementedError


class Deserialize(Protocol[T_value_cov, T_wire_contra]):
    """
    Defines the `deserialize` conversion.
    """

    def deserialize(self, data: T_wire_contra) -> T_value_cov:
        raise NotImplementedError


T_value = TypeVar("T_value")


class Serializer(Protocol[T_value, T_wire], Serialize[T_value, T_wire], Deserialize[T_value, T_wire]):
    """
    Combines `serialize` and `deserialize` in one protocol.
    """
