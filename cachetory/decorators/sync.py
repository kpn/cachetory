from datetime import timedelta
from functools import wraps
from typing import Callable, Optional, Union

from typing_extensions import ParamSpec

from cachetory.caches.sync import Cache
from cachetory.decorators import shared
from cachetory.interfaces.serializers import ValueT

P = ParamSpec("P")
"""
Original wrapped function parameter specification.
"""


def cached(
    cache: Union[Cache[ValueT], Callable[..., Cache[ValueT]]],  # no way to use `P` here
    *,
    make_key: Callable[..., str] = shared.make_default_key,  # no way to use `P` here
    time_to_live: Optional[timedelta] = None,
    if_not_exists: bool = False,
) -> Callable[[Callable[P, ValueT]], Callable[P, ValueT]]:
    """
    Args:
        cache:
            `Cache` instance or a callable tha returns a `Cache` instance for each function call.
            In the latter case the specified callable gets called with a wrapped function as the first argument,
            and the rest of the arguments next to it.
        make_key: callable to generate a custom cache key per each call.
        if_not_exists: controls concurrent sets: if `True` – avoids overwriting a cached value.
        time_to_live: cached value expiration time.
    """

    def wrap(callable_: Callable[P, ValueT]) -> Callable[P, ValueT]:
        @wraps(callable_)
        def cached_callable(*args: P.args, **kwargs: P.kwargs) -> ValueT:
            cache_ = cache(callable_, *args, **kwargs) if callable(cache) else cache
            key_ = make_key(callable_, *args, **kwargs)
            try:
                value = cache_[key_]
            except KeyError:
                value = callable_(*args, **kwargs)
                cache_.set(key_, value, time_to_live=time_to_live, if_not_exists=if_not_exists)
            return value

        return cached_callable

    return wrap
