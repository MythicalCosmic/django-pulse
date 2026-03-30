from django.dispatch import Signal

from ..entry_type import EntryType
from ..recorder import Recorder
from .base import BaseWatcher

# Django's built-in signals that should NOT be recorded - they fire constantly
# and would flood the dashboard with thousands of useless entries.
_IGNORED_SIGNAL_NAMES = {
    # Model signals (fire on every ORM save/delete/init)
    "django.db.models.signals.pre_init",
    "django.db.models.signals.post_init",
    "django.db.models.signals.pre_save",
    "django.db.models.signals.post_save",
    "django.db.models.signals.pre_delete",
    "django.db.models.signals.post_delete",
    "django.db.models.signals.m2m_changed",
    # Migration signals
    "django.db.models.signals.pre_migrate",
    "django.db.models.signals.post_migrate",
    # Request lifecycle signals
    "django.core.signals.request_started",
    "django.core.signals.request_finished",
    "django.core.signals.got_request_exception",
    # Connection signals
    "django.db.backends.signals.connection_created",
    # Auth signals
    "django.contrib.auth.signals.user_logged_in",
    "django.contrib.auth.signals.user_logged_out",
    "django.contrib.auth.signals.user_login_failed",
    # Settings signal
    "django.test.signals.setting_changed",
}


def _build_signal_identity_map():
    """Build a map from signal id() to fully qualified name for fast lookups."""
    identity = {}
    try:
        from django.db.models import signals as model_signals
        for attr_name in dir(model_signals):
            obj = getattr(model_signals, attr_name, None)
            if isinstance(obj, Signal):
                identity[id(obj)] = f"{model_signals.__name__}.{attr_name}"
    except Exception:
        pass
    try:
        from django.core import signals as core_signals
        for attr_name in dir(core_signals):
            obj = getattr(core_signals, attr_name, None)
            if isinstance(obj, Signal):
                identity[id(obj)] = f"{core_signals.__name__}.{attr_name}"
    except Exception:
        pass
    try:
        from django.db.backends import signals as backend_signals
        for attr_name in dir(backend_signals):
            obj = getattr(backend_signals, attr_name, None)
            if isinstance(obj, Signal):
                identity[id(obj)] = f"{backend_signals.__name__}.{attr_name}"
    except Exception:
        pass
    try:
        from django.contrib.auth import signals as auth_signals
        for attr_name in dir(auth_signals):
            obj = getattr(auth_signals, attr_name, None)
            if isinstance(obj, Signal):
                identity[id(obj)] = f"{auth_signals.__name__}.{attr_name}"
    except Exception:
        pass
    try:
        from django.test import signals as test_signals
        for attr_name in dir(test_signals):
            obj = getattr(test_signals, attr_name, None)
            if isinstance(obj, Signal):
                identity[id(obj)] = f"{test_signals.__name__}.{attr_name}"
    except Exception:
        pass
    return identity


class EventWatcher(BaseWatcher):
    """Records Django signal dispatches, ignoring Django's internal signals."""

    _original_send = None
    _original_send_robust = None
    _signal_names = {}  # id(signal) -> "module.name"
    _ignored_signal_ids = set()  # id(signal) for signals to skip

    def register(self):
        # Build the signal identity map
        EventWatcher._signal_names = _build_signal_identity_map()

        # Pre-compute set of signal ids to ignore for fast O(1) checks
        EventWatcher._ignored_signal_ids = {
            sig_id
            for sig_id, name in EventWatcher._signal_names.items()
            if name in _IGNORED_SIGNAL_NAMES
        }

        EventWatcher._original_send = Signal.send
        EventWatcher._original_send_robust = Signal.send_robust
        Signal.send = self._patched_send
        Signal.send_robust = self._patched_send_robust

    @staticmethod
    def _get_signal_name(signal_instance):
        sig_id = id(signal_instance)
        name = EventWatcher._signal_names.get(sig_id)
        if name:
            return name
        # Unknown signal — try to get a useful repr
        return repr(signal_instance)

    @staticmethod
    def _should_ignore(signal_instance, sender):
        """Return True if this signal should NOT be recorded."""
        # Fast check: is this a known Django internal signal?
        if id(signal_instance) in EventWatcher._ignored_signal_ids:
            return True

        # Skip telescope's own signals
        sender_name = sender.__name__ if isinstance(sender, type) else str(sender)
        if "telescope" in sender_name.lower():
            return True

        return False

    @staticmethod
    def _patched_send(signal_self, sender, **named):
        result = EventWatcher._original_send(signal_self, sender, **named)
        if not EventWatcher._should_ignore(signal_self, sender):
            EventWatcher._record_event(signal_self, sender, result)
        return result

    @staticmethod
    def _patched_send_robust(signal_self, sender, **named):
        result = EventWatcher._original_send_robust(signal_self, sender, **named)
        if not EventWatcher._should_ignore(signal_self, sender):
            EventWatcher._record_event(signal_self, sender, result)
        return result

    @staticmethod
    def _record_event(signal_instance, sender, responses):
        signal_name = EventWatcher._get_signal_name(signal_instance)
        receivers = []
        for item in (responses or []):
            if isinstance(item, tuple) and len(item) == 2:
                _, func = item
                if callable(func):
                    receivers.append(f"{func.__module__}.{func.__qualname__}")

        tags = [f"signal:{signal_name}"]

        content = {
            "signal": signal_name,
            "sender": sender.__name__ if isinstance(sender, type) else str(sender),
            "receivers": receivers,
            "receiver_count": len(receivers),
        }

        Recorder.record(entry_type=EntryType.EVENT, content=content, tags=tags)
