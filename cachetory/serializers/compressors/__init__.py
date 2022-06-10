try:
    from .zstd import ZstdCompressor  # noqa
except ImportError:
    pass  # only available with `zstd` feature
