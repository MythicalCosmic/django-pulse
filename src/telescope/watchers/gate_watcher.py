from ..entry_type import EntryType
from ..recorder import Recorder
from .base import BaseWatcher


class GateWatcher(BaseWatcher):
    """Records permission checks."""

    _original_has_perm = None

    def register(self):
        try:
            from django.contrib.auth.backends import ModelBackend

            GateWatcher._original_has_perm = ModelBackend.has_perm
            ModelBackend.has_perm = self._patched_has_perm
        except ImportError:
            pass

    @staticmethod
    def _patched_has_perm(backend_self, user_obj, perm, obj=None):
        result = GateWatcher._original_has_perm(backend_self, user_obj, perm, obj)

        tags = [f"permission:{perm}", "granted" if result else "denied"]
        if user_obj:
            tags.append(f"user:{user_obj.pk}")

        content = {
            "user": str(user_obj),
            "user_id": getattr(user_obj, "pk", None),
            "permission": perm,
            "result": result,
            "object": repr(obj) if obj else None,
        }

        Recorder.record(entry_type=EntryType.GATE, content=content, tags=tags)
        return result
