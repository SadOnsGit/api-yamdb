import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import Category


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(
            os.path.join(settings.BASE_DIR, "static", "data", "category.csv"),
            "r",
            encoding="utf-8",
        ) as f:
            csv_reader = csv.reader(f, delimiter=",")
            next(csv_reader)
            for row in csv_reader:
                try:
                    Category.objects.create(
                        id=int(row[0]),
                        name=row[1],
                        slug=row[2],
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Ошибка при добавлении категории {row[1]}: {e}"
                        )
                    )
