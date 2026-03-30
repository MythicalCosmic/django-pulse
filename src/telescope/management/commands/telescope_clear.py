from django.core.management.base import BaseCommand

from telescope.entry_type import EntryType
from telescope.pruning import clear_entries


class Command(BaseCommand):
    help = "Clear all telescope entries"

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            type=str,
            default=None,
            help="Only clear entries of this type (e.g. 'request', 'query')",
        )

    def handle(self, *args, **options):
        entry_type = None
        type_slug = options["type"]
        if type_slug:
            try:
                entry_type = EntryType.from_slug(type_slug).value
            except (KeyError, ValueError):
                self.stderr.write(self.style.ERROR(f"Invalid type: {type_slug}"))
                return

        count = clear_entries(entry_type=entry_type)
        self.stdout.write(self.style.SUCCESS(f"Cleared {count} telescope entries"))
