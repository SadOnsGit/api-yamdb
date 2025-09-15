import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import Genre, Title


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(
            os.path.join(
                settings.BASE_DIR, "static", "data", "genre_title.csv"
            ),
            "r",
            encoding="utf-8",
        ) as f:
            csv_reader = csv.reader(f, delimiter=",")
            next(csv_reader, None)
            for row in csv_reader:
                title_id = int(row[1])
                genre_id = int(row[2])
                try:
                    title = Title.objects.get(id=title_id)
                    genre = Genre.objects.get(id=genre_id)
                    title.genre.add(genre)
                except Title.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Произведение с ID {title_id} не найдено"
                        )
                    )
                except Genre.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f"Жанр с ID {genre_id} не найден")
                    )
