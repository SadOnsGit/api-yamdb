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
            "Обязательное поле. Введите верный email адрес, мы отправим код на него."
        ),
        error_messages={
            "unique": ("Такой email адрес уже зарегистрирован в системе. Пожалуйста, войдите в аккаунт"),
        },
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(username__iexact='me'),
                name='username_not_me',
                violation_error_message="Username 'me' is not allowed."
            )
        ]


class OtpCode(models.Model):
    email = models.EmailField(
        verbose_name='E-mail',
        unique=True
    )
    code = models.CharField(
        max_length=6,
        verbose_name='Единоразовый код'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    expired = models.DateTimeField(
        'Дата истечения кода'
    )
