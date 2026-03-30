import json
import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer

logger = logging.getLogger("telescope.consumers")


class TelescopeConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for real-time telescope entry updates."""

    async def connect(self):
        await self.channel_layer.group_add("telescope", self.channel_name)
        await self.accept()
        logger.debug("Telescope WebSocket connected: %s", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("telescope", self.channel_name)
        logger.debug("Telescope WebSocket disconnected: %s", self.channel_name)

    async def receive_json(self, content, **kwargs):
        # Client can send filter preferences
        msg_type = content.get("type")
        if msg_type == "filter":
            # Store filter preferences on the consumer instance
            self._filters = content.get("filters", {})

    async def telescope_entry(self, event):
        """Handle new telescope entry broadcast."""
        entry = event.get("entry", {})

        # Apply client-side filters if set
        if hasattr(self, "_filters") and self._filters:
            entry_type = entry.get("type_slug")
            allowed_types = self._filters.get("types")
            if allowed_types and entry_type not in allowed_types:
                return

        await self.send_json({"type": "entry", "data": entry})
