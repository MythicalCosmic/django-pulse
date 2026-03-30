import logging
import time

from ..entry_type import EntryType
from ..recorder import Recorder

logger = logging.getLogger("telescope.patches")

_original_execute_command = None


def patch_redis():
    global _original_execute_command
    try:
        import redis

        _original_execute_command = redis.StrictRedis.execute_command
        redis.StrictRedis.execute_command = _patched_execute_command
    except ImportError:
        logger.debug("redis-py not installed, RedisWatcher disabled")


def _patched_execute_command(self, *args, **options):
    command = args[0] if args else "UNKNOWN"
    start = time.perf_counter()

    try:
        result = _original_execute_command(self, *args, **options)
        return result
    finally:
        duration_ms = (time.perf_counter() - start) * 1000

        tags = [f"redis:{command}"]
        if duration_ms > 100:
            tags.append("slow")

        content = {
            "command": str(command),
            "args": [str(a) for a in args[1:5]],  # First few args only
            "duration": round(duration_ms, 2),
            "connection": str(getattr(self, "connection_pool", "")),
        }

        Recorder.record(entry_type=EntryType.REDIS, content=content, tags=tags)
