# Shortcuts

Sometimes, cache construction may become too wordy for a simple task. Consider this:

```python
from cachetory.backends.sync import DummyBackend
from cachetory.caches.sync import Cache
from cachetory.serializers import NoopSerializer

dummy_cache: Cache[int, int] = Cache(
    serializer=NoopSerializer(),
    backend=DummyBackend(),
)
```

This subpackage provides shortcuts for a few common cases:

## Synchronous

::: cachetory.shortcuts.sync
    options:
      heading_level: 3
      show_root_heading: false

## Asynchronous

::: cachetory.shortcuts.async_
    options:
      heading_level: 3
      show_root_heading: false
