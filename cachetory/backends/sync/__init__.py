from typing import Any
from urllib.parse import urlparse

from cachetory.interfaces.backends.sync import SyncBackend

from .dummy import DummyBackend
from .memory import MemoryBackend

try:
    from .redis import RedisBackend
except ImportError:
    RedisBackend = None  # type: ignore[assignment, misc]

try:
    from .django import DjangoBackend
except ImportError:
    DjangoBackend = None  # type: ignore[assignment, misc]


def from_url(url: str) -> SyncBackend[Any]:
    """
    Create a synchronous backend from the given URL.

    Examples:
        >>> from_url("redis://localhost:6379")
    """
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    if scheme == "memory":
        return MemoryBackend.from_url(url)
    if scheme in ("redis", "rediss", "redis+unix"):
        if RedisBackend is None:
            raise ValueError(f"`{scheme}://` requires `cachetory[redis]` extra")  # pragma: no cover
        return RedisBackend.from_url(url)
    if scheme == "dummy":
        return DummyBackend.from_url(url)
    if scheme == "django":
        if DjangoBackend is None:
            raise ValueError(f"`{scheme}://` requires `cachetory[django]` extra")  # pragma: no cover
        return DjangoBackend.from_url(url)
    raise ValueError(f"`{scheme}://` is not supported")
