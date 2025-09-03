from django.db import models


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
        max_length=200,
        db_index=True,
    )
    year = models.IntegerField(
        db_index=True
    )
    description = models.TextField(
        max_length=200,
        null=True,
    )

    class Meta:
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name[:10]


class Category(models.Model):
    '''Модель категорий.'''
    name = models.CharField(
        max_length=200,
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        db_index=True,
    )

    class Meta:
        ordering = ('name',)

    def __str__(self) -> str:
        return self.slug[:10]


class Genre(models.Model):
    '''Модель жанров.'''
    name = models.CharField(max_length=200,)
    slug = models.SlugField(max_length=100, unique=True,)

    def __str__(self) -> str:
        return self.slug[:10]


class TitleGenre(models.Model):
    '''Название жанра.'''
    title = models.ForeignKey(Title, on_delete=models.CASCADE,)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE,)

    def __str__(self) -> str:
        return f'{self.title},{self.genre}'
