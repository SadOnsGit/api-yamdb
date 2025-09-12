import datetime as dt

from django.forms import ValidationError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api_yamdb.settings import START_YEAR

from reviews.constans import (
    MIN_SCORE,
    MAX_SCORE,
    MIN_YEAR_PUB,
    CHAR_FIELD_MAX_LENGTH,
    SLUG_FIELD_MAX_LENGTH,
)

User = get_user_model()
SCORE_MIN = 1
SCORE_MAX = 10


def current_year():
    return dt.datetime.today().year


def validate_year(year):
    """Валидация поля year."""
    current_year = dt.datetime.today().year
    if not (START_YEAR <= year <= current_year):
        raise ValidationError('Год не подходит')


class Title(models.Model):
    """Модель произведений."""
    category = models.ForeignKey(
        'Category',
        related_name='titles',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    genre = models.ManyToManyField(
        'Genre',
        db_index=True,
    )
    name = models.CharField(
        max_length=CHAR_FIELD_MAX_LENGTH,
        db_index=True,
    )
    year = models.SmallIntegerField(
        db_index=True,
        validators=[MinValueValidator(
            MIN_YEAR_PUB,
            message=f'Год выпуска не может быть раньше {MIN_YEAR_PUB}'
        ), validate_year],
    )
    description = models.CharField(
        max_length=256,
        blank=True,
    )


    class Meta:
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name[:10]


class NameSlug(models.Model):
    name = models.CharField(
        max_length=CHAR_FIELD_MAX_LENGTH, verbose_name='имя',
        unique=True
    )
    slug = models.SlugField(
        max_length=SLUG_FIELD_MAX_LENGTH, verbose_name='идентификатор',
        unique=True
    )

    class Meta:
        abstract = True
        ordering = ('name',)
        verbose_name = 'имя и идентификатор'
        verbose_name_plural = 'Имена и идентификаторы'

    def __str__(self):
        return self.name


class Category(NameSlug):
    """Модель категорий."""
    class Meta(NameSlug.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Genre(NameSlug):
    """Модель жанров."""
    class Meta(NameSlug.Meta):
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Review(models.Model):
    """Отзыв на произведение.

    Пользователь может оставить не более одного отзыва на одно произведение.
    Оценка — целое число в диапазоне от 1 до 10.
    """

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
        help_text='Связь с произведением (Title).'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Текст отзыва',
        help_text='Введите текст отзыва'
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                MIN_SCORE,
                message='Оценка не может быть меньше 1'
            ),
            MaxValueValidator(
                MAX_SCORE,
                message='Оценка не может быть больше 10'
            ),
        ],
        verbose_name='Оценка',
        help_text=f'От {SCORE_MIN} до {SCORE_MAX}',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        # Свежие отзывы показываются первыми
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review_per_title',
            )
        ]

    def __str__(self):
        return f'Отзыв {self.author} на {self.title} (оценка {self.score})'


class Comment(models.Model):
    """Комментарий к отзыву.

    Комментарии удаляются вместе с отзывом.
    """

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['pub_date']

    def __str__(self):
        return f'Комментарий {self.author} к отзыву {self.review_id}'
