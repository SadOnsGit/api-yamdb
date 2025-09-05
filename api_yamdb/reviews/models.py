"""Модели Review (отзыв) и Comment (комментарий к конкретному отзыву).

На данный момент используются заглушки:
1. Review.title_id: int вместо FK на Title
2. Review.author_id: int вместо FK на User
3. Comment.author_id: int вместо FK на User
Позже, когда появятся модели User и Title, int-поля будут изменены.
"""
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    """Отзыв на произведение.

    Пользователь может оставить не более одного отзыва на одно произведение.
    Оценка — целое число в диапазоне от 1 до 10.
    """

    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
        help_text='Связь с произведением (Title).'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Текст отзыва',
        help_text='Введите текст отзыва'
    )
    # Ограничивается допустимый диапазон
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message='Оценка не может быть меньше 1'),
            MaxValueValidator(10, message='Оценка не может быть больше 10'),
        ],
        verbose_name='Оценка',
        help_text='От 1 до 10'
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
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
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
