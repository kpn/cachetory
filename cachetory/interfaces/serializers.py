from typing import TypeVar

from typing_extensions import Protocol

T_value_cov = TypeVar("T_value_cov", covariant=True)
T_value_contra = TypeVar("T_value_contra", contravariant=True)

T_wire_cov = TypeVar("T_wire_cov", covariant=True)
T_wire_contra = TypeVar("T_wire_contra", contravariant=True)


class Serializer(Protocol[T_value_contra, T_wire_cov]):
    def serialize(self, value: T_value_contra) -> T_wire_cov:
        raise NotImplementedError


class Deserializer(Protocol[T_value_cov, T_wire_contra]):
    def deserialize(self, data: T_wire_contra) -> T_value_cov:
        raise NotImplementedError
