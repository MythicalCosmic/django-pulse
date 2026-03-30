from .base import BaseWatcher


class ClientRequestWatcher(BaseWatcher):
    """Records outgoing HTTP requests (requests/httpx)."""

    def register(self):
        from ..patches.http_client_patch import patch_http_clients

        patch_http_clients()
