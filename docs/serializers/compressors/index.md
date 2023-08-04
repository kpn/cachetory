# Compressors

**Compressor** is a partial case of serializer: it's a serializer from `#!python bytes` into and from `#!python bytes`, which by definition provides some kind of data compression.

!!! tip ""

    It also means that you can use a compressor _alone_, effectively making a cache of compressed blobs:

    ```python
    from datetime import timedelta

    from cachetory.caches.sync import Cache
    from cachetory.serializers.compressors import ZlibCompressor
    from cachetory.backends.sync import RedisBackend

    cache = Cache[bytes](
        serializer=ZlibCompressor(),
        backend=RedisBackend(...),
    )
    cache.set(
        "my-blob",
        b"this huge blob will be compressed and stored in Redis for an hour",
        time_to_live=timedelta(hours=1),
    )
    ```
