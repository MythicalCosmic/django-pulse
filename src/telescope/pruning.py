from datetime import timedelta

from django.utils import timezone

from .models import TelescopeEntry
from .settings import get_config


def prune_entries(hours=None):
    """Delete telescope entries older than the configured lifetime."""
    if hours is None:
        hours = get_config("ENTRY_LIFETIME_HOURS")

    cutoff = timezone.now() - timedelta(hours=hours)
    deleted_count, _ = TelescopeEntry.objects.filter(created_at__lt=cutoff).delete()
    return deleted_count


def clear_entries(entry_type=None):
    """Delete all telescope entries, optionally filtered by type."""
    qs = TelescopeEntry.objects.all()
    if entry_type is not None:
        qs = qs.filter(type=entry_type)
    deleted_count, _ = qs.delete()
    return deleted_count
