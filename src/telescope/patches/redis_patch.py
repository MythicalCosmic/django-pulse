import logging
import time

from ..entry_type import EntryType
from ..recorder import Recorder

logger = logging.getLogger("telescope.patches")

_original_execute_command = None
_original_django_redis_execute_command = None


def patch_redis():
    """Patch both raw redis-py and django-redis to capture all Redis commands."""
    global _original_execute_command, _original_django_redis_execute_command

    patched_any = False

    # 1. Patch raw redis-py (redis.StrictRedis / redis.Redis)
    try:
        import redis
        _original_execute_command = redis.StrictRedis.execute_command
        redis.StrictRedis.execute_command = _patched_execute_command
        patched_any = True
        logger.debug("Patched redis.StrictRedis.execute_command")
    except ImportError:
        pass

    # 2. Patch django-redis DefaultClient if available
    try:
        from django_redis.client import DefaultClient
        _original_django_redis_execute_command = DefaultClient.execute_command
        DefaultClient.execute_command = _patched_django_redis_execute_command
        patched_any = True
        logger.debug("Patched django_redis.client.DefaultClient.execute_command")
    except (ImportError, AttributeError):
        pass

    # 3. Try patching django-redis herd client too
    try:
        from django_redis.client import HerdClient
        if hasattr(HerdClient, "execute_command"):
            HerdClient.execute_command = _patched_django_redis_execute_command
            logger.debug("Patched django_redis.client.HerdClient.execute_command")
    except (ImportError, AttributeError):
        pass

    if not patched_any:
        logger.debug("Neither redis-py nor django-redis installed, RedisWatcher disabled")


def _patched_execute_command(self, *args, **options):
    command = args[0] if args else "UNKNOWN"
    start = time.perf_counter()

    try:
        result = _original_execute_command(self, *args, **options)
        return result
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        _record_redis_command(command, args[1:5], duration_ms, str(getattr(self, "connection_pool", "")))


def _patched_django_redis_execute_command(self, *args, **options):
    command = args[0] if args else "UNKNOWN"
    start = time.perf_counter()

    try:
        result = _original_django_redis_execute_command(self, *args, **options)
        return result
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        conn_info = ""
        try:
            client = getattr(self, "_client", None) or getattr(self, "client", None)
            if client:
                conn_info = str(getattr(client, "connection_pool", ""))
        except Exception:
            pass
        _record_redis_command(command, args[1:5], duration_ms, conn_info)


def _record_redis_command(command, args_slice, duration_ms, connection_info):
    try:
        tags = [f"redis:{command}"]
        if duration_ms > 100:
            tags.append("slow")

        content = {
            "command": str(command),
            "args": [str(a) for a in args_slice],
            "duration": round(duration_ms, 2),
            "connection": connection_info,
        }

        Recorder.record(entry_type=EntryType.REDIS, content=content, tags=tags)
    except Exception:
        # Never let recording break the app
        pass
