from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import ADMIN_ROLE, MAX_ROLE_LENGTH, MODERATOR_ROLE, USER_ROLE, USERNAME_MAX_LENGTH
from .validators import validate_username


class NewUser(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = ADMIN_ROLE, ("Admin")
        MODERATOR = MODERATOR_ROLE, ("Moderator")
        USER = USER_ROLE, ("User")

    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=[validate_username],
        error_messages={
            "unique": ("Пользователь с таким username уже существует!"),
        },
    )
    bio = models.TextField(blank=True, verbose_name="Биография")
    role = models.CharField(
        max_length=MAX_ROLE_LENGTH,
        default=Role.USER,
        choices=Role.choices,
        verbose_name="Роль",
    )
    email = models.EmailField(
        unique=True,
        verbose_name="E-mail",
        help_text=(
            "Обязательное поле. Введите верный email адрес, "
            "мы отправим код на него."
        ),
        error_messages={
            "unique": (
                "Такой email адрес уже зарегистрирован в системе. "
                "Пожалуйста, войдите в аккаунт"
            ),
        },
    )

    @property
    def is_admin(self):
        return self.role == ADMIN_ROLE or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        return self.role == MODERATOR_ROLE

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(username__iexact="me"),
                name="username_not_me",
                violation_error_message="Username 'me' is not allowed.",
            )
        ]


class OtpCode(models.Model):
    email = models.EmailField(verbose_name="E-mail", unique=True)
    code = models.CharField(max_length=6, verbose_name="Единоразовый код")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    expired = models.DateTimeField("Дата истечения кода")
