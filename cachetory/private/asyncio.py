from typing import Callable, TypeVar

from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


async def postpone(f: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
    """Postpones `f` until awaited and forwards the value back to the caller."""
    return f(*args, **kwargs)
