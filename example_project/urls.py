import logging
from django.http import JsonResponse, HttpResponse
from django.urls import include, path
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import telescope

logger = logging.getLogger(__name__)


def index(request):
    return HttpResponse("""
    <html>
    <body style="font-family: sans-serif; max-width: 600px; margin: 40px auto; line-height: 1.6;">
        <h1>Telescope Example App</h1>
        <p>Hit these endpoints to generate telescope data:</p>
        <ul>
            <li><a href="/api/users/">/api/users/</a> — List users (generates queries)</li>
            <li><a href="/api/create-user/">/api/create-user/</a> — Create a user (model event)</li>
            <li><a href="/api/error/">/api/error/</a> — Trigger an exception</li>
            <li><a href="/api/slow/">/api/slow/</a> — Slow endpoint (~500ms)</li>
            <li><a href="/api/dump/">/api/dump/</a> — Test telescope.dump()</li>
            <li><a href="/api/log/">/api/log/</a> — Generate log entries</li>
            <li><a href="/api/cache/">/api/cache/</a> — Cache operations (set/get/delete/incr)</li>
            <li><a href="/api/redis/">/api/redis/</a> — Raw Redis operations</li>
        </ul>
        <p><a href="/telescope/" style="font-size: 1.2em; font-weight: bold;">Open Telescope Dashboard</a></p>
    </body>
    </html>
    """)


def list_users(request):
    users = list(User.objects.values("id", "username", "email", "date_joined"))
    for user in users:
        User.objects.filter(id=user["id"]).exists()
    return JsonResponse({"users": users, "count": len(users)}, json_dumps_params={"default": str})


def create_user(request):
    import uuid
    username = f"user_{uuid.uuid4().hex[:8]}"
    user = User.objects.create_user(username=username, email=f"{username}@example.com", password="test1234")
    return JsonResponse({"created": {"id": user.id, "username": user.username}})


def error_view(request):
    raise ValueError("This is a deliberate test exception!")


def slow_view(request):
    import time
    time.sleep(0.5)
    return JsonResponse({"message": "This took a while!", "delay_ms": 500})


def dump_view(request):
    data = {"key": "value", "numbers": [1, 2, 3], "nested": {"a": True}}
    telescope.dump(data, label="Example dump")
    telescope.dump(request.META.get("HTTP_USER_AGENT", "unknown"), label="User Agent")
    return JsonResponse({"message": "Dumped some data, check Telescope!"})


def log_view(request):
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    return JsonResponse({"message": "Generated 4 log entries"})


def cache_view(request):
    from django.core.cache import cache
    import uuid

    # Set some values
    key = f"test_{uuid.uuid4().hex[:6]}"
    cache.set(key, {"hello": "world", "number": 42}, timeout=60)
    cache.set("counter", 0, timeout=300)

    # Get (hit)
    val = cache.get(key)

    # Get (miss)
    miss = cache.get("nonexistent_key_xyz")

    # Increment
    cache.incr("counter")

    # has_key
    exists = cache.has_key(key)

    # get_many
    many = cache.get_many([key, "counter", "nonexistent"])

    # Delete
    cache.delete(key)

    return JsonResponse({
        "message": "Exercised cache operations",
        "set_key": key,
        "get_hit": val,
        "get_miss": miss,
        "exists": exists,
        "get_many_keys": list(many.keys()),
    }, json_dumps_params={"default": str})


def redis_view(request):
    import redis as redis_lib

    r = redis_lib.StrictRedis(host="127.0.0.1", port=6379, db=2, decode_responses=True)

    # Basic operations
    r.set("telescope:test", "hello_world")
    val = r.get("telescope:test")
    r.incr("telescope:counter")
    r.lpush("telescope:list", "item1", "item2", "item3")
    items = r.lrange("telescope:list", 0, -1)
    r.expire("telescope:test", 60)
    r.delete("telescope:list")

    return JsonResponse({
        "message": "Exercised raw Redis operations",
        "get": val,
        "list_items": items,
    })


urlpatterns = [
    path("", index),
    path("api/users/", list_users),
    path("api/create-user/", create_user),
    path("api/error/", error_view),
    path("api/slow/", slow_view),
    path("api/dump/", dump_view),
    path("api/log/", log_view),
    path("api/cache/", cache_view),
    path("api/redis/", redis_view),
    path("telescope/", include("telescope.urls")),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
