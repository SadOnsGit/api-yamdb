import re

from django.core.exceptions import ValidationError


def validate_username(value):
    """
    Валидация Username пользователя по паттерну
    отправка недопустимых символов пользователю.
    """
    if value.lower() == "me":
        raise ValidationError('Имя пользователя не может быть "me".')
    allowed_pattern = r"^[\w.@+-]+\Z"
    if not re.match(allowed_pattern, value):
        invalid_chars = re.sub(r"[\w.@+-]", "", value)
        invalid_chars = "".join(sorted(set(invalid_chars)))
        raise ValidationError(
            f"Имя пользователя содержит недопустимые символы: {invalid_chars}. "
            "Разрешены только буквы, цифры и символы @/./+/-/_."
        )
