from datetime import timedelta
from typing import Any
from unittest import mock

from pytest import fixture

from cachetory.backends.sync import MemoryBackend
from cachetory.caches.sync import Cache
from cachetory.decorators.sync import cached
from cachetory.serializers import NoopSerializer


@fixture
def cache() -> Cache[int, int]:
    return Cache(serializer=NoopSerializer(), backend=MemoryBackend[int]())


@fixture
def cache_2() -> Cache[int, int]:
    return Cache(serializer=NoopSerializer(), backend=MemoryBackend[int]())


def test_simple(cache: Cache[int, int]):
    call_counter = 0

    @cached(cache)
    def expensive_function(arg: int, *, kwarg: int) -> int:
        assert arg == 1, "the positional argument is not forwarded"
        assert kwarg == 2, "the keyword argument is not forwarded"
        nonlocal call_counter
        call_counter += 1
        return 42

    assert expensive_function(1, kwarg=2) == 42, "the return value is not forwarded"
    assert call_counter == 1
    expensive_function(1, kwarg=2)
    assert call_counter == 1, "cache did not work"


def test_time_to_live_callable_depending_on_key(cache: Cache[int, int]):
    """time_to_live accepts the key as a keyword argument, allowing for different expirations."""

    def ttl(key: str) -> timedelta:
        if "a=a" in key:
            return timedelta(seconds=42)
        return timedelta(seconds=1)

    @cached(cache, time_to_live=ttl)
    def expensive_function(**kwargs: Any) -> int:
        return 1

    with mock.patch.object(cache, "set", wraps=cache.set) as m_set:
        assert expensive_function(a="a") == 1

    m_set.assert_called_with(mock.ANY, mock.ANY, time_to_live=timedelta(seconds=42), if_not_exists=mock.ANY)
