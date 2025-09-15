import datetime as dt

from rest_framework.exceptions import ValidationError


def validate_year(year):
    """Валидация поля year."""
    current_year = dt.datetime.today().year
    if not (year <= current_year):
        raise ValidationError("Год не подходит")
