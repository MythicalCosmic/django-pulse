import time

from ..entry_type import EntryType
from ..recorder import Recorder
from .base import BaseWatcher

TRACKED_METHODS = ("get", "set", "delete", "clear", "get_many", "set_many", "delete_many", "has_key", "incr", "decr")


class CacheWatcher(BaseWatcher):
    """Records cache operations by wrapping methods on each configured cache instance.

    Works with any cache backend (django-redis, memcached, file, locmem, etc.)
    by patching the actual cache objects from django.core.cache.caches.
    """

    def register(self):
        from django.core.cache import caches
        from django.conf import settings

        # Patch each configured cache backend
        for alias in settings.CACHES:
            try:
                cache = caches[alias]
                self._patch_cache_instance(cache, alias)
            except Exception:
                pass

    def _patch_cache_instance(self, cache, alias):
        """Wrap each cache method on this specific instance."""
        for method_name in TRACKED_METHODS:
            original = getattr(cache, method_name, None)
            if original is None:
                continue
            # Don't double-patch
            if getattr(original, "_telescope_patched", False):
                continue
            wrapped = _make_wrapper(method_name, original, alias)
            setattr(cache, method_name, wrapped)


def _make_wrapper(method_name, original, alias):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = None
        try:
            result = original(*args, **kwargs)
            return result
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            try:
                _record(method_name, args, kwargs, result, duration_ms, alias)
            except Exception:
                pass
    wrapper._telescope_patched = True
    wrapper.__name__ = method_name
    return wrapper


def _record(operation, args, kwargs, result, duration_ms, backend_alias):
    key = None
    value = None
    hit = None

    if operation in ("get", "has_key"):
        key = str(args[0]) if args else None
        if operation == "get":
            default = args[1] if len(args) > 1 else kwargs.get("default")
            hit = result is not None and result != default
    elif operation == "set":
        key = str(args[0]) if args else None
        value = repr(args[1])[:512] if len(args) > 1 else None
    elif operation == "delete":
        key = str(args[0]) if args else None
    elif operation == "get_many":
        key = str(args[0]) if args else None
        hit = bool(result) if result is not None else None
    elif operation == "set_many":
        key = str(list(args[0].keys())) if args and isinstance(args[0], dict) else None
    elif operation == "delete_many":
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
