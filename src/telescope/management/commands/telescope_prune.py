from django.core.management.base import BaseCommand

from telescope.pruning import prune_entries
from telescope.settings import get_config


class Command(BaseCommand):
    help = "Prune old telescope entries"

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=None,
            help=f"Delete entries older than N hours (default: {get_config('ENTRY_LIFETIME_HOURS')})",
        )

    def handle(self, *args, **options):
        hours = options["hours"]
        count = prune_entries(hours=hours)
        self.stdout.write(self.style.SUCCESS(f"Pruned {count} telescope entries"))
