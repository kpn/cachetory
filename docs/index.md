# Quickstart

=== "Sync"

    ```python
    from cachetory import serializers
    from cachetory.backends import sync as sync_backends
    from cachetory.caches.sync import Cache


    cache = Cache[int, bytes](
        serializer=serializers.from_url("pickle://"),
        backend=sync_backends.from_url("redis://localhost:6379"),
    )
    with cache:
        cache.set("foo", 42)
        assert cache.get("foo") == 42
    ```

=== "Async"

    ```python
    from cachetory import serializers
    from cachetory.backends import async_ as async_backends
    from cachetory.caches.async_ import Cache


    cache = Cache[int, bytes](
        serializer=serializers.from_url("pickle://?pickle-protocol=4"),
        backend=async_backends.from_url("redis://localhost:6379"),
    )
    async with cache:
        await cache.set("foo", 42)
        assert await cache.get("foo") == 42
    ```

!!! tip

    It is perfectly fine not to use the context manager if, for example, you need a cache instance to live through the entire application lifetime:

    ```python
    # caches.py:
    cache = Cache(...)

    # app.py:
    from caches import cache
    await cache.set("foo", 42)
    ```
