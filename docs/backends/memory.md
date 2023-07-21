# Memory

Simple memory backend that stores values in a plain dictionary.

## Supported URLs

- `memory://`

!!! warning "Caveats"

    - This backend does **not** copy values. Meaning that mutating a stored value mutates it in the backend too. If this is not desirable, consider using another serializer or making up your own serializer which copies values in its `serialize` method.
    - Expired items actually get deleted **only** when accessed. If you put a value into the backend and never try to retrieve it – it'll stay in memory forever.

---

::: cachetory.backends.sync.MemoryBackend
    options:
      heading_level: 2

---

::: cachetory.backends.async_.MemoryBackend
    options:
      heading_level: 2
