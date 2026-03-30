import pytest
from telescope.entry_type import EntryType
from telescope.models import TelescopeEntry, TelescopeEntryTag


@pytest.mark.django_db
class TestTelescopeEntry:
    def test_create_entry(self):
        entry = TelescopeEntry.objects.create(
            type=EntryType.REQUEST.value,
            content={"method": "GET", "path": "/test/"},
        )
        assert entry.uuid is not None
        assert entry.type == EntryType.REQUEST.value
        assert entry.content["method"] == "GET"

    def test_entry_type_property(self):
        entry = TelescopeEntry.objects.create(
            type=EntryType.QUERY.value,
            content={"sql": "SELECT 1"},
        )
        assert entry.entry_type == EntryType.QUERY

    def test_entry_tags(self):
        entry = TelescopeEntry.objects.create(
            type=EntryType.REQUEST.value,
            content={},
        )
        TelescopeEntryTag.objects.create(entry=entry, tag="status:200")
        TelescopeEntryTag.objects.create(entry=entry, tag="slow")

        tags = list(entry.tags.values_list("tag", flat=True))
        assert "status:200" in tags
        assert "slow" in tags
