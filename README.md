# Django Scope

An elegant, real-time debug assistant for Django. Inspired by [Laravel Telescope](https://laravel.com/docs/telescope) — built from the ground up for Django.

Django Scope gives you a beautiful dashboard to monitor everything happening in your application: requests, database queries, exceptions, model changes, cache operations, Redis commands, log entries, and much more. Unlike traditional debug tools that dump information into your terminal or a toolbar on the page, Django Scope provides a standalone SPA dashboard with **real-time WebSocket updates** — you see entries appear the instant they happen, no refresh needed.

## Why Django Scope?

### vs. Django Debug Toolbar

| | Django Debug Toolbar | Django Scope |
|---|---|---|
| **Interface** | Panel injected into HTML responses | Standalone dashboard (works with APIs, SPAs, mobile backends) |
| **Real-time** | No — only shows data for the current page load | Yes — WebSocket-powered live feed |
| **API requests** | Cannot inspect (no HTML to inject into) | Full request/response capture for all endpoints |
| **Background tasks** | Not supported | Commands, schedules, batches |
| **Persistence** | Gone on page refresh | Stored in database, browsable history |
| **N+1 detection** | Manual inspection of query list | Automatic detection with threshold alerts |
| **Cache/Redis** | Limited cache panel | Full operation-level cache + raw Redis command tracking |
| **Exceptions** | Not tracked | Full stack traces with source context |
| **Production safe** | Not recommended | Authorization gate, pruning, toggle recording |

### vs. Silk

| | Silk | Django Scope |
|---|---|---|
| **Scope** | Requests + queries only | 17 watchers (requests, queries, cache, Redis, mail, models, logs, exceptions, events, commands, dumps, HTTP client, views, gates, notifications, schedules, batches) |
| **Real-time** | No — must refresh to see new data | WebSocket live feed |
| **Frontend** | Basic server-rendered HTML | Modern Vue.js SPA with dark/light themes and animations |
| **Cache/Redis** | Not tracked | Full auto-detection, no config needed |
| **Model changes** | Not tracked | Field-level change tracking on save/delete |
| **N+1 detection** | Not built-in | Automatic with configurable threshold |

### vs. Sentry / New Relic / Datadog

Those are production monitoring and error tracking platforms (and great at what they do). Django Scope is a **development and debugging tool** — it's local, free, instant, and shows you everything at the code level without sending data to a third party. Use Django Scope during development, use Sentry in production. They complement each other.

## Features

- **17 watchers** covering every aspect of your Django application
- **Real-time WebSocket updates** — entries appear instantly in the dashboard
- **N+1 query detection** — automatically flags repeated query patterns
- **Slow query highlighting** — configurable threshold (default: 100ms)
- **Beautiful Vue.js dashboard** with dark and light themes
- **Auto-detection** — cache and Redis monitoring works automatically, no backend swapping required
- **Request-scoped buffering** — entries are grouped by request with a single bulk write for minimal performance impact
- **Zero config for basics** — add the app, add the middleware, done
- **Authorization gate** — control who can access the dashboard
- **Pruning** — automatic cleanup of old entries

## Quick Start

### 1. Install

```bash
pip install django-scope
```

### 2. Add to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    "daphne",          # Required for WebSocket support
    # ... your apps
    "telescope",
]
```

> **Note:** `daphne` must be listed before `django.contrib.staticfiles` (if present) so it can serve the ASGI application. If you don't need real-time WebSocket updates, you can skip `daphne` and run under WSGI — the dashboard will still work, just without live updates.

### 3. Add the middleware

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "telescope.middleware.TelescopeMiddleware",
    # ... other middleware
]
```

### 4. Add URL routing

```python
from django.urls import include, path

urlpatterns = [
    path("telescope/", include("telescope.urls")),
    # ... your urls
]
```

### 5. Configure ASGI (for real-time WebSocket updates)

Create or update your `asgi.py`:

```python
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from telescope.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(websocket_urlpatterns),
})
```

And in your settings:

```python
ASGI_APPLICATION = "myproject.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}
```

### 6. Run migrations

```bash
python manage.py migrate
```

### 7. Open the dashboard

Start your server and visit `http://localhost:8000/telescope/`.

## Configuration

All configuration lives in a single `TELESCOPE` dictionary in your Django settings:

```python
TELESCOPE = {
    # Master switch — disable to completely turn off Django Scope
    "ENABLED": True,

    # Toggle recording without disabling (can be toggled from the dashboard)
    "RECORDING": True,

    # URL paths to ignore (regex patterns)
    "IGNORE_PATHS": [r"^/telescope/", r"^/static/", r"^/favicon\.ico$"],

    # HTTP methods to ignore
    "IGNORE_METHODS": [],  # e.g. ["OPTIONS", "HEAD"]

    # Status codes to ignore
    "IGNORE_STATUS_CODES": [],  # e.g. [304]

    # Queries slower than this are flagged as "slow" (milliseconds)
    "SLOW_QUERY_THRESHOLD": 100,

    # Flag N+1 when the same query pattern repeats this many times in one request
    "N_PLUS_ONE_THRESHOLD": 5,

    # Auto-prune entries older than this
    "ENTRY_LIFETIME_HOURS": 24,

    # Max size per entry payload (KB)
    "ENTRY_SIZE_LIMIT": 64,

    # Authorization callback — controls who can access the dashboard
    # Receives the request, returns True/False. Defaults to settings.DEBUG.
    "AUTHORIZATION": lambda request: request.user.is_superuser,

    # Enable/disable individual watchers
    "WATCHERS": {
        "RequestWatcher":       {"enabled": True},
        "QueryWatcher":         {"enabled": True},
        "ExceptionWatcher":     {"enabled": True},
        "ModelWatcher":         {"enabled": True},
        "LogWatcher":           {"enabled": True},
        "CacheWatcher":         {"enabled": True},
        "RedisWatcher":         {"enabled": False},  # Opt-in
        "MailWatcher":          {"enabled": True},
        "ViewWatcher":          {"enabled": True},
        "EventWatcher":         {"enabled": True},
        "CommandWatcher":       {"enabled": True},
        "DumpWatcher":          {"enabled": True},
        "ClientRequestWatcher": {"enabled": False},  # Opt-in
        "GateWatcher":          {"enabled": True},
        "NotificationWatcher":  {"enabled": True},
        "ScheduleWatcher":      {"enabled": False},  # Requires Celery
        "BatchWatcher":         {"enabled": False},   # Requires Celery
    },
}
```

## The 17 Watchers

### Request Watcher

Captures every HTTP request and response — method, path, headers, payload, response body, status code, duration, the resolved view function, and the user/session.

### Query Watcher

Records every database query with SQL, bindings, execution time, and connection alias. Automatically detects:

- **Slow queries** — flagged when execution exceeds `SLOW_QUERY_THRESHOLD` (default 100ms)
- **N+1 queries** — flagged when the same query pattern repeats `N_PLUS_ONE_THRESHOLD` times (default 5) in a single request

Works with any Django database backend (SQLite, PostgreSQL, MySQL, etc.) via Django's `connection_created` signal — every new database connection gets instrumented automatically.

### Exception Watcher

Captures unhandled exceptions with the full stack trace, exception class, message, and the file/line where it occurred. Connects to Django's `got_request_exception` signal.

### Model Watcher

Tracks model create, update, and delete operations via Django's `pre_save`, `post_save`, and `post_delete` signals. Records field-level changes on updates (old value vs. new value).

### Log Watcher

Captures log entries from Python's `logging` module — all levels (DEBUG through CRITICAL). Installs a custom handler on the root logger so it catches logs from your code and third-party libraries alike.

### Cache Watcher

Monitors all cache operations: `get`, `set`, `delete`, `clear`, `get_many`, `set_many`, `delete_many`, `has_key`, `incr`, `decr`. Records the key, value, hit/miss status, duration, and backend alias.

**Auto-detection** — works with any cache backend out of the box. No need to swap your `CACHES` backend setting. Works with `django-redis`, memcached, file cache, database cache, local memory cache, and any custom backend.

### Redis Watcher

Captures raw Redis commands (`SET`, `GET`, `LPUSH`, `EXPIRE`, etc.) with arguments, duration, and connection info. Supports both:

- **`redis-py`** — patches `StrictRedis.execute_command`
- **`django-redis`** — patches `DefaultClient` for Django cache operations that go through Redis

Enable it in settings:

```python
"RedisWatcher": {"enabled": True},
```

### Mail Watcher

Records outgoing emails — recipients, subject, body (HTML and plain text), and attachments. Uses a wrapping email backend.

### View Watcher

Tracks template rendering — which templates are rendered, render duration, and the resolved view.

### Event Watcher

Records Django signal dispatches. Automatically ignores Django's internal signals (`pre_save`, `post_save`, `request_started`, `connection_created`, etc.) to avoid flooding. Only records your custom signals and third-party signals.

### Command Watcher

Captures management command execution — command name, arguments, exit code, output, and duration.

### Dump Watcher

A `telescope.dump()` function you can call from anywhere in your code to inspect values:

```python
import telescope

def my_view(request):
    telescope.dump(some_complex_object, label="Debug: user data")
    telescope.dump(request.headers, label="Request headers")
    # ...
```

Each dump records the value, label, and the exact file/line where `dump()` was called.

### Client Request Watcher

Monitors outgoing HTTP requests made by your application (via `requests` or `httpx`). Records URL, method, status code, headers, and duration.

### Gate Watcher

Tracks permission checks — records which user, which permission, and whether it was granted or denied.

### Notification Watcher

Records notifications sent to users — notification class, recipient, and delivery channels.

### Schedule Watcher

Tracks Celery Beat scheduled task execution (requires Celery).

### Batch Watcher

Monitors Celery group/chord batch job execution (requires Celery).

## Management Commands

### Prune old entries

```bash
# Prune entries older than the configured lifetime (default: 24 hours)
python manage.py telescope_prune

# Prune entries older than 6 hours
python manage.py telescope_prune --hours 6
```

### Clear all entries

```bash
# Clear everything
python manage.py telescope_clear

# Clear only query entries
python manage.py telescope_clear --type query

# Clear only exceptions
python manage.py telescope_clear --type exception
```

You can also clear entries from the dashboard UI — each list page has a clear button.

## Running Without WebSockets (WSGI)

If you can't run an ASGI server, Django Scope still works. The dashboard will function normally — you just won't get real-time live updates. The WebSocket indicator will show "Disconnected" and stop retrying after a few attempts. Data is still recorded and visible when you refresh or navigate.

Skip `daphne` from `INSTALLED_APPS` and the ASGI/channels configuration. Everything else stays the same.

## Authorization

By default, the dashboard is only accessible when `DEBUG = True`. For more control, set an authorization callback:

```python
TELESCOPE = {
    "AUTHORIZATION": lambda request: request.user.is_staff,
}
```

Or a more complex check:

```python
def scope_authorized(request):
    if not request.user.is_authenticated:
        return False
    return request.user.email.endswith("@mycompany.com")

TELESCOPE = {
    "AUTHORIZATION": scope_authorized,
}
```

## Database

Django Scope creates 3 tables:

- `telescope_entries` — all recorded entries (UUID, type, JSON content, batch ID, timestamps)
- `telescope_entries_tags` — searchable tags (e.g. `slow`, `n+1`, `status:500`, `cache:hit`)
- `telescope_monitoring` — selective monitoring configuration

All entry data is stored as JSON, keeping the schema simple and the queries fast.

## Performance

Django Scope is designed to have minimal impact on your application:

- **Request-scoped buffering** — entries are collected in memory during a request and written in a single `bulk_create` at the end, not one INSERT per event
- **Re-entrancy guard** — Django Scope's own database operations are never recorded (no infinite loops)
- **Path filtering** — Dashboard routes and static files are excluded by default
- **Async-safe** — uses `contextvars` (not `threading.local`) so it works correctly with Django's async views
- **Configurable pruning** — old entries are automatically cleaned up

## Requirements

- Python 3.10+
- Django 4.2+
- `channels` 4.0+ (for WebSocket support)
- `daphne` (recommended, for ASGI server)

Optional:
- `redis` / `django-redis` (for Redis watcher)
- `celery` (for Schedule and Batch watchers)

## License

MIT
