from typing import Any

from pytest import fixture, mark

from cachetory.backends.async_ import MemoryBackend
from cachetory.caches.async_ import Cache
from cachetory.decorators.async_ import cached
from cachetory.serializers import NoopSerializer


@fixture
def cache() -> Cache[int]:
    return Cache(serializer=NoopSerializer(), backend=MemoryBackend[int]())


@fixture
def cache_2() -> Cache[int]:
    return Cache(serializer=NoopSerializer(), backend=MemoryBackend[int]())


@mark.asyncio
async def test_simple(cache: Cache[int]):
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


@mark.asyncio
async def test_callable_cache(cache: Cache[int], cache_2: Cache[int]):
    call_counter = 0

    async def choose_cache(_wrapped_callable: Any, param: int) -> Cache[int]:
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
