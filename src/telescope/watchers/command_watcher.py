import time

from ..entry_type import EntryType
from ..recorder import Recorder
from .base import BaseWatcher


class CommandWatcher(BaseWatcher):
    """Records management command executions."""

    _original_execute = None

    def register(self):
        from django.core.management.base import BaseCommand

        CommandWatcher._original_execute = BaseCommand.execute
        BaseCommand.execute = self._patched_execute

    @staticmethod
    def _patched_execute(command_self, *args, **options):
        start = time.perf_counter()
        exit_code = 0
        output = None

        try:
            output = CommandWatcher._original_execute(command_self, *args, **options)
            return output
        except SystemExit as e:
            exit_code = e.code if e.code else 0
            raise
        except Exception as e:
            exit_code = 1
            raise
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            command_name = command_self.__class__.__module__.split(".")[-1]

            # Skip telescope's own commands
            if command_name.startswith("telescope"):
                return

            tags = [f"command:{command_name}"]
            if exit_code != 0:
                tags.append("error")

            content = {
                "command": command_name,
                "arguments": {k: str(v) for k, v in (options or {}).items() if k not in ("stderr", "stdout")},
                "exit_code": exit_code,
                "duration": round(duration_ms, 2),
                "output": str(output)[:2048] if output else None,
            }

            Recorder.record(entry_type=EntryType.COMMAND, content=content, tags=tags)
