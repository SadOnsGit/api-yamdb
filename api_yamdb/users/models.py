from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOICES = (
    ('user', 'User'),
    ('moderator', 'Moderator'),
    ('admin', 'Admin'),
)


class CustomUser(AbstractUser):
    password = models.CharField(
        max_length=128,
        blank=True,
        null=True,
    )
    bio = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Биография'
    )
    role = models.CharField(
        default='user',
        choices=ROLE_CHOICES,
        verbose_name='Роль'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='E-mail',
        help_text=
        (
            "Обязательное поле. Введите верный email адрес, его нужно будет подтвердить."
        ),
        error_messages={
            "unique": ("Такой email адрес уже зарегистрирован в системе. Пожалуйста, войдите в аккаунт"),
        },
    )
