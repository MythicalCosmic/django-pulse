import logging

from ..entry_type import EntryType
from ..recorder import Recorder
from .base import BaseWatcher

logger = logging.getLogger("telescope.watchers")


class ScheduleWatcher(BaseWatcher):
    """Records Celery Beat scheduled tasks."""

    def register(self):
        try:
            from celery.signals import beat_init, task_prerun, task_postrun

            beat_init.connect(self._on_beat_init)
            task_prerun.connect(self._on_task_prerun)
            task_postrun.connect(self._on_task_postrun)
        except ImportError:
            logger.debug("Celery not installed, ScheduleWatcher disabled")

    def _on_beat_init(self, sender, **kwargs):
        pass

    def _on_task_prerun(self, sender=None, task_id=None, task=None, args=None, kwargs=None, **kw):
        content = {
            "task": str(task),
            "task_id": task_id,
            "args": str(args),
            "kwargs": str(kwargs),
            "status": "running",
        }
        Recorder.record(entry_type=EntryType.SCHEDULE, content=content, tags=[f"task:{task}"])

    def _on_task_postrun(self, sender=None, task_id=None, task=None, retval=None, state=None, **kw):
        content = {
            "task": str(task),
            "task_id": task_id,
            "status": state or "completed",
            "result": str(retval)[:512] if retval else None,
        }
        tags = [f"task:{task}", f"status:{state}"]
        Recorder.record(entry_type=EntryType.SCHEDULE, content=content, tags=tags)
