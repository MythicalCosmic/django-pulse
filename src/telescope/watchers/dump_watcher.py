from .base import BaseWatcher


class DumpWatcher(BaseWatcher):
    """Records dump() calls. Driven by the public telescope.dump() API."""

    def register(self):
        # Dump watcher is driven by the public telescope.dump() function
        pass
