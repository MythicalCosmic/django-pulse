from .base import BaseWatcher


class NotificationWatcher(BaseWatcher):
    """Records notifications. Driven by the public telescope.notify() API."""

    def register(self):
        # Notification watcher is driven by the public telescope.notify() function
        pass
