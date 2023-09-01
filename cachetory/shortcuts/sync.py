from __future__ import annotations

from cachetory.backends.sync import DummyBackend, MemoryBackend
from cachetory.caches.sync import Cache
from cachetory.interfaces.serializers import ValueT
from cachetory.serializers import NoopSerializer


def dummy_cache() -> Cache[ValueT, ValueT]:  # pragma: no cover
    """Instantiate and return a dummy cache without a serializer."""
    return Cache[ValueT, ValueT](serializer=NoopSerializer(), backend=DummyBackend())


def memory_cache() -> Cache[ValueT, ValueT]:  # pragma: no cover
    """Instantiate and return a local memory cache without a serializer."""
    return Cache[ValueT, ValueT](serializer=NoopSerializer(), backend=MemoryBackend())
