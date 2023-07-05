from __future__ import annotations

from datetime import timedelta
from functools import wraps
from typing import Awaitable, Callable, Optional, Union

from typing_extensions import ParamSpec

from cachetory.caches.async_ import Cache
from cachetory.decorators import shared
from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.serializers import ValueT
from cachetory.private.functools import into_async_callable

P = ParamSpec("P")
"""
Original wrapped function parameter specification.
"""


def cached(
    cache: Union[
        Cache[ValueT, WireT],
        Callable[..., Cache[ValueT, WireT]],
        Callable[..., Awaitable[Cache[ValueT, WireT]]],
    ],  # no way to use `P` here
    *,
    make_key: Callable[..., str] = shared.make_default_key,  # no way to use `P` here
    time_to_live: Optional[timedelta | Callable[..., timedelta] | Callable[..., Awaitable[timedelta]]] = None,
    if_not_exists: bool = False,
    exclude: Callable[[str, ValueT], bool] | Callable[[str, ValueT], Awaitable[bool]] | None = None,
) -> Callable[[Callable[P, Awaitable[ValueT]]], Callable[P, Awaitable[ValueT]]]:
    """
    Apply memoization to the wrapped callable.

    Args:
        cache:
            `Cache` instance or a callable (sync or async) that returns a `Cache` instance for each function call.
            In the latter case the specific callable gets called with a wrapped function as the first argument,
            and the rest of the arguments next to it.
        make_key: callable to generate a custom cache key per each call.
        time_to_live:
            cached value expiration time or a callable (sync or async) that returns the expiration time.
            The callable needs to accept keyword arguments, and it is given the cache key to
            compute the expiration time.
        if_not_exists: controls concurrent sets: if `True` – avoids overwriting a cached value.
        exclude: Optional callable to prevent a key-value pair from being cached if the callable returns true.
    """

    def wrap(callable_: Callable[P, Awaitable[ValueT]]) -> Callable[P, Awaitable[ValueT]]:
        get_cache = into_async_callable(cache)
        get_time_to_live = into_async_callable(time_to_live)
        exclude_ = into_async_callable(exclude)  # type: ignore[arg-type]

        @wraps(callable_)
        async def cached_callable(*args: P.args, **kwargs: P.kwargs) -> ValueT:
            cache_ = await get_cache(callable_, *args, **kwargs)
            key_ = make_key(callable_, *args, **kwargs)
            time_to_live_ = await get_time_to_live(key=key_)

            value = await cache_.get(key_)
            if value is None:
                value = await callable_(*args, **kwargs)
                if exclude is None or not await exclude_(key_, value):
                    await cache_.set(key_, value, time_to_live=time_to_live_, if_not_exists=if_not_exists)
            return value

        return cached_callable

    return wrap
