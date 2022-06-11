from urllib.parse import urlparse

from cachetory.interfaces.backends.async_ import AsyncBackend

from .dummy import AsyncDummyBackend
from .memory import AsyncMemoryBackend

try:
    # noinspection PyUnresolvedReferences
    from .redis import AsyncRedisBackend
except ImportError:
    is_redis_available = False
else:
    is_redis_available = True


async def from_url(url: str) -> AsyncBackend:
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    if scheme == "memory":
        return await AsyncMemoryBackend.from_url(url)
    if scheme in ("redis", "rediss") and is_redis_available:
        return await AsyncRedisBackend.from_url(url)
    if scheme == "redis+unix" and is_redis_available:
        return await AsyncRedisBackend.from_url(url[6:])  # unix://…
    if scheme == "dummy":
        return await AsyncDummyBackend.from_url(url)
    raise ValueError(f"`{scheme}://` is not supported")
