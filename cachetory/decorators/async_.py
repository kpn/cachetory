from datetime import timedelta
from functools import wraps
from typing import Awaitable, Callable, Optional, Union

from typing_extensions import ParamSpec

from cachetory.caches.async_ import Cache
from cachetory.decorators import shared
from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.serializers import ValueT

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
    time_to_live: Optional[Union[timedelta, Callable[..., timedelta], Callable[..., Awaitable[timedelta]]]] = None,
    if_not_exists: bool = False,
) -> Callable[[Callable[P, Awaitable[ValueT]]], Callable[P, Awaitable[ValueT]]]:
    """
    Apply memoization to the wrapped callable.

    Args:
        cache:
            `Cache` instance or an callable (sync or async) that returns a `Cache` instance for each function call.
            In the latter case the specific callable gets called with a wrapped function as the first argument,
            and the rest of the arguments next to it.
        make_key: callable to generate a custom cache key per each call.
        if_not_exists: controls concurrent sets: if `True` – avoids overwriting a cached value.
        time_to_live:
            cached value expiration time or a callable (sync or async) that returns the expiration time.
            The callable needs to accept keyword arguments, and it is given the cache key to
            compute the expiration time.
    """

    def wrap(callable_: Callable[P, Awaitable[ValueT]]) -> Callable[P, Awaitable[ValueT]]:
        @wraps(callable_)
        async def cached_callable(*args: P.args, **kwargs: P.kwargs) -> ValueT:
            cache_ = (
                cache if not callable(cache) else await shared.call_sync_or_async(cache, callable_, *args, **kwargs)
            )
            key_ = make_key(callable_, *args, **kwargs)

            time_to_live_ = (
                time_to_live if not callable(time_to_live) else await shared.call_sync_or_async(time_to_live, key=key_)
            )

            value = await cache_.get(key_)
            if value is None:
                value = await callable_(*args, **kwargs)
                await cache_.set(key_, value, time_to_live=time_to_live_, if_not_exists=if_not_exists)
            return value

        return cached_callable

    return wrap
