import pytest
from django.test import Client


@pytest.mark.django_db
class TestTelescopeMiddleware:
    def test_request_is_recorded(self):
        from telescope.models import TelescopeEntry
        from telescope.entry_type import EntryType
        from telescope.watchers import WatcherRegistry

        WatcherRegistry.register_all()

        client = Client()
        response = client.get("/test/")
        assert response.status_code == 200

        # Should have recorded a request entry
        request_entries = TelescopeEntry.objects.filter(type=EntryType.REQUEST.value)
        assert request_entries.count() == 1

        entry = request_entries.first()
        assert entry.content["method"] == "GET"
        assert entry.content["path"] == "/test/"
        assert entry.content["status_code"] == 200

    def test_telescope_paths_ignored(self):
        from telescope.models import TelescopeEntry
        from telescope.entry_type import EntryType
        from telescope.watchers import WatcherRegistry

        WatcherRegistry.register_all()

        client = Client()
        # This should be ignored
        response = client.get("/telescope/api/status")
        # The view may or may not exist, but the middleware should skip it
        entries = TelescopeEntry.objects.filter(type=EntryType.REQUEST.value)
        assert entries.count() == 0


@pytest.mark.django_db
class TestRequestDuration:
    def test_duration_is_recorded(self):
        from telescope.models import TelescopeEntry
        from telescope.entry_type import EntryType
        from telescope.watchers import WatcherRegistry

        WatcherRegistry.register_all()

        client = Client()
        client.get("/test/")

        entry = TelescopeEntry.objects.filter(type=EntryType.REQUEST.value).first()
        assert entry is not None
        assert entry.content["duration"] > 0
