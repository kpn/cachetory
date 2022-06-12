from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.serializers import Serializer, T_value

from .chained import ChainedSerializer
from .noop import NoopSerializer  # noqa
from .pickle import PickleSerializer  # noqa


def from_url(url: str) -> Serializer[T_value, WireT]:
    return ChainedSerializer[T_value, WireT].from_url(url)
