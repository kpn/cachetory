from cachetory.interfaces.backends.shared import T_wire
from cachetory.interfaces.serializers import Serializer, T_value

from .chained import ChainedSerializer
from .noop import NoopSerializer  # noqa
from .pickle import PickleSerializer  # noqa


def from_url(url: str) -> Serializer[T_value, T_wire]:
    return ChainedSerializer[T_value, T_wire].from_url(url)
