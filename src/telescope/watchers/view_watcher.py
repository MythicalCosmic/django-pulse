import time

from ..entry_type import EntryType
from ..recorder import Recorder
from .base import BaseWatcher


class ViewWatcher(BaseWatcher):
    """Records template rendering."""

    _original_render = None

    def register(self):
        from django.template.base import Template

        ViewWatcher._original_render = Template.render
        Template.render = self._patched_render

    @staticmethod
    def _patched_render(template_self, context):
        start = time.perf_counter()
        result = ViewWatcher._original_render(template_self, context)
        duration_ms = (time.perf_counter() - start) * 1000

        template_name = getattr(template_self, "name", None) or "<inline>"

        tags = [f"template:{template_name}"]
        if duration_ms > 100:
            tags.append("slow")

        content = {
            "template": template_name,
            "duration": round(duration_ms, 2),
        }

        Recorder.record(entry_type=EntryType.VIEW, content=content, tags=tags)
        return result
