import time

from django.core.cache.backends.locmem import LocMemCache


class TelescopeCacheBackend(LocMemCache):
    """Wrapping cache backend that records all cache operations."""

    def __init__(self, server, params):
        # The actual backend class to wrap can be specified in OPTIONS
        self._telescope_alias = params.get("telescope_alias", "default")
        actual_backend = params.pop("TELESCOPE_BACKEND", None)

        if actual_backend:
            # Dynamically instantiate the real backend
            from django.utils.module_loading import import_string

            backend_cls = import_string(actual_backend)
            self._real_cache = backend_cls(server, params)
        else:
            super().__init__(server, params)
            self._real_cache = None

    def _get_backend(self):
        return self._real_cache if self._real_cache else self

    def get(self, key, default=None, version=None):
        start = time.perf_counter()
        backend = self._get_backend()
        if backend is self:
            value = super().get(key, default, version)
        else:
            value = backend.get(key, default, version)
        duration_ms = (time.perf_counter() - start) * 1000

        from ..watchers.cache_watcher import CacheWatcher

        CacheWatcher.record_operation(
            operation="get",
            key=key,
            value=value,
            hit=value is not default,
            duration_ms=duration_ms,
            backend_alias=self._telescope_alias,
        )
        return value

    def set(self, key, value, timeout=None, version=None):
        start = time.perf_counter()
        backend = self._get_backend()
        if backend is self:
            result = super().set(key, value, timeout, version)
        else:
            result = backend.set(key, value, timeout, version)
        duration_ms = (time.perf_counter() - start) * 1000

        from ..watchers.cache_watcher import CacheWatcher

        CacheWatcher.record_operation(
            operation="set",
            key=key,
            value=value,
            duration_ms=duration_ms,
            backend_alias=self._telescope_alias,
        )
        return result

    def delete(self, key, version=None):
        start = time.perf_counter()
        backend = self._get_backend()
        if backend is self:
            result = super().delete(key, version)
        else:
            result = backend.delete(key, version)
        duration_ms = (time.perf_counter() - start) * 1000

        from ..watchers.cache_watcher import CacheWatcher

        CacheWatcher.record_operation(
            operation="delete",
            key=key,
            duration_ms=duration_ms,
            backend_alias=self._telescope_alias,
        )
        return result

    def clear(self):
        backend = self._get_backend()
        if backend is self:
            result = super().clear()
        else:
            result = backend.clear()

        from ..watchers.cache_watcher import CacheWatcher

        CacheWatcher.record_operation(operation="clear", key="*")
        return result
