import pytest
from django.test import Client, override_settings

from telescope.entry_type import EntryType
from telescope.models import TelescopeEntry

TELESCOPE_SETTINGS = {
    "ENABLED": True,
    "AUTHORIZATION": lambda request: True,
}


@pytest.mark.django_db
class TestApiEndpoints:
    def _create_entries(self):
        # Clear any entries from watchers first
        TelescopeEntry.objects.all().delete()

        for i in range(5):
            TelescopeEntry.objects.create(
                type=EntryType.REQUEST.value,
                content={"method": "GET", "path": f"/test/{i}/", "status_code": 200, "duration": 10},
            )
        TelescopeEntry.objects.create(
            type=EntryType.QUERY.value,
            content={"sql": "SELECT 1", "duration": 5},
        )
        TelescopeEntry.objects.create(
            type=EntryType.EXCEPTION.value,
            content={"class": "ValueError", "message": "test"},
        )

    @override_settings(TELESCOPE=TELESCOPE_SETTINGS)
    def test_entry_list(self):
        self._create_entries()
        client = Client()
        response = client.get("/telescope/api/entries")
        assert response.status_code == 200
        data = response.json()
        assert len(data["entries"]) >= 7  # May have extra from watchers

    @override_settings(TELESCOPE=TELESCOPE_SETTINGS)
    def test_typed_entry_list(self):
        self._create_entries()
        client = Client()
        response = client.get("/telescope/api/entries/request")
        assert response.status_code == 200
        data = response.json()
        assert len(data["entries"]) == 5

    @override_settings(TELESCOPE=TELESCOPE_SETTINGS)
    def test_entry_detail(self):
        entry = TelescopeEntry.objects.create(
            type=EntryType.REQUEST.value,
            content={"method": "POST", "path": "/api/"},
        )
        client = Client()
        response = client.get(f"/telescope/api/entry/{entry.uuid}")
        assert response.status_code == 200
        data = response.json()
        assert data["entry"]["content"]["method"] == "POST"

    @override_settings(TELESCOPE=TELESCOPE_SETTINGS)
    def test_entry_not_found(self):
        client = Client()
        response = client.get("/telescope/api/entry/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    @override_settings(TELESCOPE=TELESCOPE_SETTINGS)
    def test_status_endpoint(self):
        self._create_entries()
        client = Client()
        response = client.get("/telescope/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["total_entries"] >= 7
        assert "request" in data["types"]

    @override_settings(TELESCOPE=TELESCOPE_SETTINGS)
    def test_clear_entries(self):
        self._create_entries()
        client = Client()
        response = client.delete("/telescope/api/clear")
        assert response.status_code == 200
        assert TelescopeEntry.objects.count() == 0

    @override_settings(TELESCOPE=TELESCOPE_SETTINGS)
    def test_clear_entries_by_type(self):
        self._create_entries()
        client = Client()
        response = client.delete("/telescope/api/clear?type=request")
        assert response.status_code == 200
        assert TelescopeEntry.objects.filter(type=EntryType.REQUEST.value).count() == 0
        assert TelescopeEntry.objects.filter(type=EntryType.QUERY.value).count() >= 1
