from django.dispatch import Signal

from ..entry_type import EntryType
from ..recorder import Recorder
from .base import BaseWatcher


class EventWatcher(BaseWatcher):
    """Records Django signal dispatches."""

    _original_send = None
    _original_send_robust = None

    def register(self):
        EventWatcher._original_send = Signal.send
        EventWatcher._original_send_robust = Signal.send_robust
        Signal.send = self._patched_send
        Signal.send_robust = self._patched_send_robust

    @staticmethod
    def _get_signal_name(signal_instance):
        # Try to find the signal's variable name from known Django signals
        from django.db.models import signals as model_signals
        from django.core import signals as core_signals

        for module in (model_signals, core_signals):
            for attr_name in dir(module):
                if getattr(module, attr_name, None) is signal_instance:
                    return f"{module.__name__}.{attr_name}"
        return repr(signal_instance)

    @staticmethod
    def _patched_send(signal_self, sender, **named):
        result = EventWatcher._original_send(signal_self, sender, **named)
        EventWatcher._record_event(signal_self, sender, result)
        return result

    @staticmethod
    def _patched_send_robust(signal_self, sender, **named):
        result = EventWatcher._original_send_robust(signal_self, sender, **named)
        EventWatcher._record_event(signal_self, sender, result)
        return result

    @staticmethod
    def _record_event(signal_instance, sender, responses):
        # Skip telescope's own signals
        sender_name = sender.__name__ if isinstance(sender, type) else str(sender)
        if "telescope" in sender_name.lower():
            return

        signal_name = EventWatcher._get_signal_name(signal_instance)
        receivers = [f"{func.__module__}.{func.__qualname__}" for _, func in (responses or []) if callable(func)]

        tags = [f"signal:{signal_name}"]

        content = {
            "signal": signal_name,
            "sender": sender_name,
            "receivers": receivers,
            "receiver_count": len(receivers),
        }

        Recorder.record(entry_type=EntryType.EVENT, content=content, tags=tags)
