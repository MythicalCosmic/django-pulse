from django.urls import path, re_path

from .views.api import (
    BatchDetailView,
    ClearEntriesView,
    EntryDeleteView,
    EntryDetailView,
    EntryListView,
    MonitoringView,
    StatusView,
    ToggleRecordingView,
    TypedEntryListView,
)
from .views.spa import TelescopeSpaView

app_name = "telescope"

urlpatterns = [
    # API endpoints
    path("api/entries", EntryListView.as_view(), name="entries-list"),
    path("api/entries/<str:type_slug>", TypedEntryListView.as_view(), name="entries-typed"),
    path("api/entry/<uuid:uuid>", EntryDetailView.as_view(), name="entry-detail"),
    path("api/entry/<uuid:uuid>/delete", EntryDeleteView.as_view(), name="entry-delete"),
    path("api/batch/<uuid:batch_id>", BatchDetailView.as_view(), name="batch-detail"),
    path("api/clear", ClearEntriesView.as_view(), name="clear"),
    path("api/status", StatusView.as_view(), name="status"),
    path("api/toggle-recording", ToggleRecordingView.as_view(), name="toggle-recording"),
    path("api/monitoring", MonitoringView.as_view(), name="monitoring"),

    # SPA catch-all — must be last
    re_path(r"^(?P<path>.*)$", TelescopeSpaView.as_view(), name="spa"),
]
