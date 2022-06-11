from urllib.parse import urlparse

from cachetory.interfaces.backends.async_ import AsyncBackend

from .dummy import AsyncDummyBackend
from .memory import AsyncMemoryBackend


async def from_url(url: str) -> AsyncBackend:
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    if scheme == "memory":
        return await AsyncMemoryBackend.from_url(url)
    if scheme == "dummy":
        return await AsyncDummyBackend.from_url(url)
    raise ValueError(f"`{scheme}://` is not supported")
