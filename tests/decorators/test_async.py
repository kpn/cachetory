from datetime import timedelta
from typing import Any
from unittest import mock

import pytest

from cachetory.backends.async_ import MemoryBackend
from cachetory.caches.async_ import Cache
from cachetory.decorators.async_ import cached
from cachetory.serializers import NoopSerializer


@pytest.fixture
def cache() -> Cache[int, int]:
    return Cache(serializer=NoopSerializer(), backend=MemoryBackend[int]())


@pytest.fixture
def cache_2() -> Cache[int, int]:
    return Cache(serializer=NoopSerializer(), backend=MemoryBackend[int]())


async def test_simple(cache: Cache[int, int]):
    call_counter = 0

    @cached(cache)
    async def expensive_function(arg: int, *, kwarg: int) -> int:
        assert arg == 1, "the positional argument is not forwarded"
        assert kwarg == 2, "the keyword argument is not forwarded"
        nonlocal call_counter
        call_counter += 1
        return 42

    assert await expensive_function(1, kwarg=2) == 42, "the return value is not forwarded"
    assert call_counter == 1
    await expensive_function(1, kwarg=2)
    assert call_counter == 1, "cache did not work"


@pytest.mark.parametrize(
    "sync_callable",
    [
        True,
        False,
    ],
)
async def test_callable_cache(cache: Cache[int, int], cache_2: Cache[int, int], sync_callable):
    call_counter = 0

    if sync_callable:

        def choose_cache(_wrapped_callable: Any, param: int) -> Cache[int, int]:
            return cache_2 if param == 2 else cache

    else:

        async def choose_cache(_wrapped_callable: Any, param: int) -> Cache[int, int]:  # type: ignore [misc]
            return cache_2 if param == 2 else cache

    @cached(cache=choose_cache)
    async def expensive_function(_: int) -> int:
        nonlocal call_counter
        call_counter += 1
        return 42

    await expensive_function(1)
    assert call_counter == 1

    await expensive_function(2)
    assert call_counter == 2

    assert cache._backend.size == 1  # type: ignore
    assert cache_2._backend.size == 1  # type: ignore


def sync_ttl(*args: Any, **kwargs: Any) -> timedelta:
    return timedelta(seconds=42)


async def async_ttl(*args: Any, **kwargs: Any) -> timedelta:
    return timedelta(seconds=42)


@pytest.mark.parametrize(
    "ttl_function",
    [
        pytest.param(sync_ttl, id="sync-callable"),
        pytest.param(async_ttl, id="async-callable"),
    ],
)
async def test_time_to_live_accepts_callable(cache: Cache[int, int], ttl_function):
    expected_time_to_live = timedelta(seconds=42)

    @cached(cache, time_to_live=ttl_function)
    async def expensive_function() -> int:
        return 1

    with mock.patch.object(cache, "set", wraps=cache.set) as m_set:
        assert await expensive_function() == 1

    # time_to_live is correctly forwarded to cache
    m_set.assert_called_with(mock.ANY, mock.ANY, time_to_live=expected_time_to_live, if_not_exists=mock.ANY)


async def test_time_to_live_callable_depending_on_key(cache: Cache[int, int]):
    """time_to_live accepts the key as a keyword argument, allowing for different expirations."""

    async def ttl(key: str) -> timedelta:
        if "a=a" in key:
            return timedelta(seconds=42)
        return timedelta(seconds=1)

    @cached(cache, time_to_live=ttl)
    async def expensive_function(**kwargs: Any) -> int:
        return 1

    with mock.patch.object(cache, "set", wraps=cache.set) as m_set:
        assert await expensive_function(a="a") == 1

    m_set.assert_called_with(mock.ANY, mock.ANY, time_to_live=timedelta(seconds=42), if_not_exists=mock.ANY)
