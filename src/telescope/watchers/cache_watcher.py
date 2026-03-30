import time

from ..entry_type import EntryType
from ..recorder import Recorder
from .base import BaseWatcher

_original_methods = {}


class CacheWatcher(BaseWatcher):
    """Records cache operations by monkey-patching BaseCache methods.

    Auto-detects any cache backend (memcached, redis, file, db, locmem, etc.)
    without requiring the user to swap their CACHES backend setting.
    """

    def register(self):
        from django.core.cache.backends.base import BaseCache

        for method_name in ("get", "set", "delete", "clear", "get_many", "set_many", "delete_many", "has_key", "incr", "decr"):
            original = getattr(BaseCache, method_name, None)
            if original and method_name not in _original_methods:
                _original_methods[method_name] = original
                patched = self._make_wrapper(method_name, original)
                setattr(BaseCache, method_name, patched)

    @staticmethod
    def _make_wrapper(method_name, original):
        def wrapper(cache_self, *args, **kwargs):
            start = time.perf_counter()
            try:
                result = original(cache_self, *args, **kwargs)
                return result
            finally:
                duration_ms = (time.perf_counter() - start) * 1000
                CacheWatcher._record(method_name, args, kwargs, result if 'result' in dir() else None, duration_ms, cache_self)
        wrapper.__name__ = method_name
        wrapper.__qualname__ = f"BaseCache.{method_name}"
        return wrapper

    @staticmethod
    def _record(operation, args, kwargs, result, duration_ms, cache_instance):
        try:
            backend_alias = getattr(cache_instance, "_alias", "default")

            # Extract key info based on operation
            key = None
            value = None
            hit = None

            if operation in ("get", "has_key"):
                key = str(args[0]) if args else None
                if operation == "get":
                    default = args[1] if len(args) > 1 else kwargs.get("default")
                    hit = result is not None and result != default
            elif operation in ("set",):
                key = str(args[0]) if args else None
                value = repr(args[1])[:512] if len(args) > 1 else None
            elif operation in ("delete",):
                key = str(args[0]) if args else None
            elif operation in ("get_many",):
                key = str(args[0]) if args else None  # list of keys
                hit = bool(result) if result is not None else None
            elif operation in ("set_many",):
                key = str(list(args[0].keys())) if args and isinstance(args[0], dict) else None
            elif operation in ("delete_many",):
                key = str(args[0]) if args else None
            elif operation in ("incr", "decr"):
                key = str(args[0]) if args else None

            tags = [f"cache:{operation}"]
            if hit is True:
                tags.append("hit")
            elif hit is False and operation == "get":
                tags.append("miss")

            content = {
                "type": operation,
                "key": key,
                "value": value,
                "hit": hit,
                "duration": round(duration_ms, 2),
                "backend": backend_alias,
            }

            Recorder.record(entry_type=EntryType.CACHE, content=content, tags=tags)
        except Exception:
            # Never let cache recording break the app
            pass
