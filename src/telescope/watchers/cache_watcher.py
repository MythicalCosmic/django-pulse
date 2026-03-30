from ..entry_type import EntryType
from ..recorder import Recorder
from .base import BaseWatcher


class CacheWatcher(BaseWatcher):
    """Records cache operations. Works with the wrapping cache backend."""

    def register(self):
        # CacheWatcher is driven by the wrapping cache backend.
        # Users must set CACHES backend to telescope.backends.cache_backend.TelescopeCacheBackend
        pass

    @classmethod
    def record_operation(cls, operation, key, value=None, hit=None, duration_ms=0, backend_alias="default"):
        tags = [f"cache:{operation}"]
        if hit is not None:
            tags.append("hit" if hit else "miss")

        content = {
            "type": operation,
            "key": str(key),
            "value": repr(value)[:512] if value is not None else None,
            "hit": hit,
            "duration": round(duration_ms, 2),
            "backend": backend_alias,
        }

        Recorder.record(entry_type=EntryType.CACHE, content=content, tags=tags)
