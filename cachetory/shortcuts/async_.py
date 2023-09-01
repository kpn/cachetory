from __future__ import annotations

from cachetory.backends.async_ import DummyBackend, MemoryBackend
from cachetory.caches.async_ import Cache
from cachetory.interfaces.serializers import ValueT
from cachetory.serializers import NoopSerializer


def dummy_cache() -> Cache[ValueT, ValueT]:  # pragma: no cover
    """Instantiate and return a dummy cache without a serializer."""
    return Cache[ValueT, ValueT](serializer=NoopSerializer(), backend=DummyBackend())


def memory_cache() -> Cache[ValueT, ValueT]:  # pragma: no cover
    """Instantiate and return a local memory cache without a serializer."""
    return Cache[ValueT, ValueT](serializer=NoopSerializer(), backend=MemoryBackend())
