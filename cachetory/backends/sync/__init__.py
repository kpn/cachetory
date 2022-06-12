from urllib.parse import urlparse

from cachetory.interfaces.backends.sync import SyncBackend

from .dummy import DummyBackend
from .memory import MemoryBackend

try:
    # noinspection PyUnresolvedReferences
    from .redis import RedisBackend
except ImportError:
    is_redis_available = False
else:
    is_redis_available = True


def from_url(url: str) -> SyncBackend:
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    if scheme == "memory":
        return MemoryBackend.from_url(url)
    if scheme in ("redis", "rediss") and is_redis_available:
        return RedisBackend.from_url(url)
    if scheme == "redis+unix" and is_redis_available:
        return RedisBackend.from_url(url[6:])  # unix://…
    if scheme == "dummy":
        return DummyBackend.from_url(url)
    raise ValueError(f"`{scheme}://` is not supported")
