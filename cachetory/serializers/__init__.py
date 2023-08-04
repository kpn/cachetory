from contextlib import suppress

from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.serializers import Serializer, ValueT

from .chained import ChainedSerializer as ChainedSerializer
from .json import JsonSerializer as JsonSerializer
from .noop import NoopSerializer as NoopSerializer
from .pickle import PickleSerializer as PickleSerializer

with suppress(ImportError):
    from .msgpack import MsgPackSerializer as MsgPackSerializer


def from_url(url: str) -> Serializer[ValueT, WireT]:
    """
    Construct a serializer from the URL.

    This is an alias for the
    [`cachetory.serializers.ChainedSerializer.from_url()`][cachetory.serializers.ChainedSerializer.from_url].
    """
    return ChainedSerializer[ValueT, WireT].from_url(url)
