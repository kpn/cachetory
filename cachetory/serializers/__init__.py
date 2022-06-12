from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.serializers import Serializer, ValueT

from .chained import ChainedSerializer
from .noop import NoopSerializer  # noqa
from .pickle import PickleSerializer  # noqa


def from_url(url: str) -> Serializer[ValueT, WireT]:
    return ChainedSerializer[ValueT, WireT].from_url(url)
