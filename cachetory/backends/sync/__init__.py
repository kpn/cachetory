from urllib.parse import urlparse

from cachetory.interfaces.backends.sync import SyncBackend

from .memory import SyncMemoryBackend
from .redis import SyncRedisBackend


def from_url(url: str) -> SyncBackend:
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    if scheme == "memory":
        return SyncMemoryBackend.from_url(url)
    if scheme in ("redis", "rediss"):
        return SyncRedisBackend.from_url(url)
    if scheme == "redis+unix":
        return SyncRedisBackend.from_url(url[6:])
    raise ValueError(f"`{scheme}://` is not supported")
