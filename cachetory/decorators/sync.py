from __future__ import annotations

from datetime import timedelta
from functools import wraps
from typing import Callable, Optional

from typing_extensions import ParamSpec

from cachetory.caches.sync import Cache
from cachetory.decorators import shared
from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.serializers import ValueT
from cachetory.private.functools import maybe_callable

P = ParamSpec("P")
"""Original wrapped function parameter specification."""


def cached(
    cache: Cache[ValueT, WireT] | Callable[..., Cache[ValueT, WireT]],  # no way to use `P` here
    *,
    make_key: Callable[..., str] = shared.make_default_key,  # no way to use `P` here
    time_to_live: Optional[timedelta | Callable[..., timedelta]] = None,
    if_not_exists: bool = False,
) -> Callable[[Callable[P, ValueT]], Callable[P, ValueT]]:
    """
    Apply memoization to the wrapped callable.

    Args:
        cache:
            `Cache` instance or a callable tha returns a `Cache` instance for each function call.
            In the latter case the specified callable gets called with a wrapped function as the first argument,
            and the rest of the arguments next to it.
        make_key: callable to generate a custom cache key per each call.
        if_not_exists: controls concurrent sets: if `True` – avoids overwriting a cached value.
        time_to_live:
            cached value expiration time or callable that returns the expiration time.
            The callable needs to accept keyword arguments, and it is given the cache key to
            compute the expiration time.
    """

    def wrap(callable_: Callable[P, ValueT]) -> Callable[P, ValueT]:
        @wraps(callable_)
        def cached_callable(*args: P.args, **kwargs: P.kwargs) -> ValueT:
            cache_ = maybe_callable(cache, callable_, *args, **kwargs)
            key_ = make_key(callable_, *args, **kwargs)
            time_to_live_ = maybe_callable(time_to_live, key=key_)

            try:
                value = cache_[key_]
            except KeyError:
                value = callable_(*args, **kwargs)
                cache_.set(key_, value, time_to_live=time_to_live_, if_not_exists=if_not_exists)
            return value

        return cached_callable

    return wrap
