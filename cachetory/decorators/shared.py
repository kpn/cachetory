from hashlib import blake2s
from typing import Any, Callable


def make_default_key(callable_: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
    """
    Generate a human-readable cache key out of decorated function fully-qualified name and stringified arguments.

    The length of the key depends on the arguments.
    """

    # noinspection PyUnresolvedReferences
    parts = (
        callable_.__module__,
        callable_.__qualname__,
        # Since we join with `:`, we need to «escape» `:`s with `::`.
        *(str(arg).replace(":", "::") for arg in args),
        *(f"{str(key).replace(':', '::')}={str(value).replace(':', '::')}" for key, value in sorted(kwargs.items())),
    )
    return ":".join(parts)


def make_default_hashed_key(callable_: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
    """
    Generate a hashed fixed-length cache key given the callable and the arguments it's being called with.

    Uses `blake2s` as the fastest algorithm from `hashlib`.
    """
    return blake2s(make_default_key(callable_, *args, **kwargs).encode()).hexdigest()
