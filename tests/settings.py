SECRET_KEY = "telescope-test-secret-key"
DEBUG = True

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "telescope",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

MIDDLEWARE = [
    "telescope.middleware.TelescopeMiddleware",
]

ROOT_URLCONF = "tests.urls"

TELESCOPE = {
    "ENABLED": True,
    "RECORDING": True,
    "IGNORE_PATHS": [r"^/telescope/", r"^/static/"],
    "WATCHERS": {
        "RequestWatcher": {"enabled": True},
        "QueryWatcher": {"enabled": True},
        "ExceptionWatcher": {"enabled": True},
        "ModelWatcher": {"enabled": True},
        "LogWatcher": {"enabled": True},
        "CacheWatcher": {"enabled": True},
        "MailWatcher": {"enabled": True},
        "ViewWatcher": {"enabled": False},
        "EventWatcher": {"enabled": False},
        "CommandWatcher": {"enabled": False},
        "DumpWatcher": {"enabled": True},
        "RedisWatcher": {"enabled": False},
        "ClientRequestWatcher": {"enabled": False},
        "GateWatcher": {"enabled": False},
        "NotificationWatcher": {"enabled": True},
        "ScheduleWatcher": {"enabled": False},
        "BatchWatcher": {"enabled": False},
    },
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
