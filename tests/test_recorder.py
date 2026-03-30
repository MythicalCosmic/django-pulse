import pytest

from telescope.context import end_scope, start_scope
from telescope.entry_type import EntryType
from telescope.models import TelescopeEntry, TelescopeEntryTag
from telescope.recorder import Recorder


@pytest.mark.django_db
class TestRecorder:
    def test_record_without_scope_writes_immediately(self):
        TelescopeEntry.objects.all().delete()  # Clear any watcher entries
        Recorder.record(
            entry_type=EntryType.DUMP,
            content={"dump": "hello"},
            tags=["test"],
        )
        entry = TelescopeEntry.objects.filter(type=EntryType.DUMP.value).first()
        assert entry is not None
        assert entry.content["dump"] == "hello"
        assert entry.tags.filter(tag="test").exists()

    def test_record_with_scope_buffers(self):
        TelescopeEntry.objects.all().delete()
        start_scope()
        Recorder.record(
            entry_type=EntryType.DUMP,
            content={"message": "buffered"},
        )
        # Not yet persisted
        assert TelescopeEntry.objects.filter(type=EntryType.DUMP.value).count() == 0

        Recorder.flush()
        assert TelescopeEntry.objects.filter(type=EntryType.DUMP.value).count() == 1
        end_scope()

    def test_flush_writes_batch_id(self):
        TelescopeEntry.objects.all().delete()
        start_scope()
        Recorder.record(entry_type=EntryType.DUMP, content={"message": "a"})
        Recorder.record(entry_type=EntryType.DUMP, content={"message": "b"})
        Recorder.flush()

        entries = TelescopeEntry.objects.filter(type=EntryType.DUMP.value)
        assert entries.count() == 2
        assert entries[0].batch_id is not None
        assert entries[0].batch_id == entries[1].batch_id
        end_scope()

    def test_record_with_tags(self):
        TelescopeEntry.objects.all().delete()
        Recorder.record(
            entry_type=EntryType.DUMP,
            content={"value": "tagged"},
            tags=["status:200", "slow"],
        )
        entry = TelescopeEntry.objects.filter(type=EntryType.DUMP.value).first()
        assert entry is not None
        tag_values = list(entry.tags.values_list("tag", flat=True))
        assert "status:200" in tag_values
        assert "slow" in tag_values
