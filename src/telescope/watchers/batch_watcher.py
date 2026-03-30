import logging

from ..entry_type import EntryType
from ..recorder import Recorder
from .base import BaseWatcher

logger = logging.getLogger("telescope.watchers")


class BatchWatcher(BaseWatcher):
    """Records Celery group/chord batch operations."""

    def register(self):
        try:
            from celery.signals import task_prerun, task_postrun

            task_prerun.connect(self._on_task_prerun)
            task_postrun.connect(self._on_task_postrun)
        except ImportError:
            logger.debug("Celery not installed, BatchWatcher disabled")

    def _on_task_prerun(self, sender=None, task_id=None, task=None, args=None, kwargs=None, **kw):
        # Detect group/chord tasks
        request = getattr(sender, "request", None)
        if request and getattr(request, "group", None):
            content = {
                "batch_id": request.group,
                "task": str(task),
                "task_id": task_id,
                "status": "running",
            }
            Recorder.record(
                entry_type=EntryType.BATCH,
                content=content,
                tags=[f"batch:{request.group}", f"task:{task}"],
            )

    def _on_task_postrun(self, sender=None, task_id=None, task=None, retval=None, state=None, **kw):
        request = getattr(sender, "request", None)
        if request and getattr(request, "group", None):
            content = {
                "batch_id": request.group,
                "task": str(task),
                "task_id": task_id,
                "status": state or "completed",
            }
            Recorder.record(
                entry_type=EntryType.BATCH,
                content=content,
                tags=[f"batch:{request.group}", f"status:{state}"],
            )
