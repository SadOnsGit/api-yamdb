from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model


User = get_user_model()


class Title(models.Model):
    '''Модель произведений.'''
    category = models.ForeignKey(
        'Category',
        related_name='titles',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        db_index=True,
    )
    genre = models.ManyToManyField(
        'Genre',
        through='TitleGenre',
        db_index=True,
    )
    name = models.CharField(
        max_length=256,
        db_index=True,
    )
    year = models.IntegerField(
        db_index=True
    )
    description = models.CharField(
        max_length=256,
        blank=True,
    )
    rating = models.IntegerField(
        default=0,
    )

    class Meta:
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name[:10]


class Category(models.Model):
    '''Модель категорий.'''
    name = models.CharField(
        max_length=256,
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        db_index=True,
    )

    class Meta:
        ordering = ('name',)

    def __str__(self) -> str:
        return self.slug[:10]


class Genre(models.Model):
    '''Модель жанров.'''
    name = models.CharField(max_length=256,)
    slug = models.SlugField(max_length=50, unique=True,)

    def __str__(self) -> str:
        return self.slug[:10]


class TitleGenre(models.Model):
    '''Название жанра.'''
    title = models.ForeignKey(Title, on_delete=models.CASCADE,)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE,)

    def __str__(self) -> str:
        return f'{self.title},{self.genre}'


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
