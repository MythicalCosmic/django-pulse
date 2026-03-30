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


urlpatterns = [
    path("", index),
    path("api/users/", list_users),
    path("api/create-user/", create_user),
    path("api/error/", error_view),
    path("api/slow/", slow_view),
    path("api/dump/", dump_view),
    path("api/log/", log_view),
    path("telescope/", include("telescope.urls")),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
