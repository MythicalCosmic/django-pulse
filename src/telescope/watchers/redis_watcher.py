from .base import BaseWatcher


class RedisWatcher(BaseWatcher):
    """Records Redis commands."""

    def register(self):
        from ..patches.redis_patch import patch_redis

        patch_redis()
