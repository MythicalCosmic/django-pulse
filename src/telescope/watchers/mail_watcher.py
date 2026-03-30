from ..entry_type import EntryType
from ..recorder import Recorder
from .base import BaseWatcher


class MailWatcher(BaseWatcher):
    """Records sent emails. Works with the wrapping mail backend."""

    def register(self):
        # MailWatcher is driven by the wrapping mail backend.
        pass

    @classmethod
    def record_mail(cls, message):
        recipients = list(message.to) if message.to else []
        tags = [f"to:{r}" for r in recipients[:5]]

        content = {
            "subject": message.subject,
            "from": message.from_email,
            "to": recipients,
            "cc": list(message.cc) if message.cc else [],
            "bcc": list(message.bcc) if message.bcc else [],
            "body": message.body[:2048] if message.body else None,
            "html_body": None,
            "attachments": [a[0] if isinstance(a, tuple) else str(a) for a in (message.attachments or [])],
        }

        # Check for HTML alternative
        if hasattr(message, "alternatives"):
            for alt_content, mimetype in message.alternatives:
                if mimetype == "text/html":
                    content["html_body"] = alt_content[:4096]
                    break

        Recorder.record(entry_type=EntryType.MAIL, content=content, tags=tags)
