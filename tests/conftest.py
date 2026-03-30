import pytest


@pytest.fixture(autouse=True)
def clean_telescope_entries(db):
    """Clean telescope entries before and after each test."""
    from telescope.models import TelescopeEntry

    TelescopeEntry.objects.all().delete()
    yield
    TelescopeEntry.objects.all().delete()
