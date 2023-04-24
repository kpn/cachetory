from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.serializers import Serializer, ValueT

from .chained import ChainedSerializer as ChainedSerializer
from .noop import NoopSerializer as NoopSerializer
from .pickle import PickleSerializer as PickleSerializer


def from_url(url: str) -> Serializer[ValueT, WireT]:
    return ChainedSerializer[ValueT, WireT].from_url(url)
