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
        verbose_name='E-mail'
    )
