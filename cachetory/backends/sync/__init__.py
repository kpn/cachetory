from urllib.parse import urlparse

from cachetory.interfaces.backends.sync import SyncBackend

from .dummy import SyncDummyBackend
from .memory import SyncMemoryBackend

try:
    # noinspection PyUnresolvedReferences
    from .redis import SyncRedisBackend
except ImportError:
    is_redis_available = False
else:
    is_redis_available = True


def from_url(url: str) -> SyncBackend:
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    if scheme == "memory":
        return SyncMemoryBackend.from_url(url)
    if scheme in ("redis", "rediss") and is_redis_available:
        return SyncRedisBackend.from_url(url)
    if scheme == "redis+unix" and is_redis_available:
        return SyncRedisBackend.from_url(url[6:])  # unix://…
    if scheme == "dummy":
        return SyncDummyBackend.from_url(url)
    raise ValueError(f"`{scheme}://` is not supported")
