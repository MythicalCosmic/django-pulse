from django.core.mail.backends.smtp import EmailBackend


class TelescopeMailBackend(EmailBackend):
    """Wrapping mail backend that records all sent emails."""

    def send_messages(self, email_messages):
        from ..watchers.mail_watcher import MailWatcher

        for message in email_messages:
            MailWatcher.record_mail(message)

        return super().send_messages(email_messages)
