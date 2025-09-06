from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast


def with_title_rating(qs):
    """Добавляет рейтинг (среднее по reviews.score)."""
    return qs.annotate(rating=Cast(Avg('reviews__score'), IntegerField()))
