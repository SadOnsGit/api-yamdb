from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Runs all CSV processing commands in the specified order."

    def handle(self, *args, **options):
        command_order = [
            "process_csv_users",
            "process_csv_category",
            "process_csv_genre",
            "process_csv_titles",
            "process_csv_genre_title",
            "process_csv_reviews",
            "process_csv_comments",
        ]
        for cmd in command_order:
            self.stdout.write(f"Running command: {cmd}")
            call_command(cmd)
            self.stdout.write(f"Completed command: {cmd}")
