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


def test_callable_cache(cache: Cache[int, int], cache_2: Cache[int, int]):
    call_counter = 0

    @cached(lambda _wrapped_callable, param: cache_2 if param == 2 else cache)
    def expensive_function(_: int) -> int:
        nonlocal call_counter
        call_counter += 1
        return 42

    expensive_function(1)
    assert call_counter == 1

    expensive_function(2)
    assert call_counter == 2

    assert cache._backend.size == 1  # type: ignore
    assert cache_2._backend.size == 1  # type: ignore


def test_time_to_live_accepts_callable(cache: Cache[int, int]):
    expected_time_to_live = timedelta(seconds=42)

    def ttl(*args: Any, **kwargs: Any) -> timedelta:
        return expected_time_to_live

    @cached(cache, time_to_live=ttl)
    def expensive_function() -> int:
        return 1

    with mock.patch.object(cache, "set", wraps=cache.set) as m_set:
        assert expensive_function() == 1

    # time_to_live is correctly forwarded to cache
    m_set.assert_called_with(mock.ANY, mock.ANY, time_to_live=expected_time_to_live, if_not_exists=mock.ANY)


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


def test_exclude(cache: Cache[int, int]):
    @cached(
        cache,
        make_key=lambda _, arg: str(arg),
        exclude=lambda key_, value_: int(key_) + value_ < 40,
    )
    def power_function(arg: int) -> int:
        return arg**2

    with mock.patch.object(cache, "set", wraps=cache.set):
        assert power_function(5) == 25
        assert power_function(6) == 36

    assert cache.get("5") is None
    assert cache.get("6") == 36
