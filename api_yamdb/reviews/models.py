from datetime import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models

from users.models import CustomUser
from .constants import (
    NAME_MAX_LENGTH,
    SLUG_MAX_LENGTH,
    MIN,
    MAX
)

User = CustomUser


class Category(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH,
                            verbose_name='Название')
    slug = models.SlugField(max_length=SLUG_MAX_LENGTH,
                            unique=True, verbose_name='Слаг')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(verbose_name='Название',
                            max_length=NAME_MAX_LENGTH, db_index=True)
    slug = models.SlugField(verbose_name='Slug',
                            max_length=SLUG_MAX_LENGTH, unique=True,
                            db_index=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


def validate_year(value):
    current_year = datetime.now().year
    if value > current_year:
        raise ValidationError(f'Год не может превышать {current_year}.')


class Title(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=256, db_index=True
    )
    year = models.SmallIntegerField(
        verbose_name='Год создания',
        validators=[validate_year],
        db_index=True,
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        related_name='titles',
        through='GenreTitle'
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='titles',
        verbose_name='Произведение'
    )
    genre = models.ForeignKey(
        Genre,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='genres',
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Жанр произведения'
        verbose_name_plural = 'Жанры произведения'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'genre'],
                name='unique_title_genre'
            )
        ]

    def __str__(self):
        return f'{self.title} - {self.genre}'


class Review(models.Model):
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(User, verbose_name='Автор',
                               related_name='reviews',
                               on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[MinValueValidator(MIN),
                    MaxValueValidator(MAX)], db_index=True)
    pub_date = models.DateTimeField(verbose_name='Дата публикации',
                                    auto_now_add=True, db_index=True)
    title = models.ForeignKey(Title, verbose_name='Произведение',
                              related_name='reviews', on_delete=models.CASCADE)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'], name='unique review'
            )
        ]

    def __str__(self):
        return self.text


class Comments(models.Model):
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(User, verbose_name='Автор',
                               related_name='comments',
                               on_delete=models.CASCADE)
    pub_date = models.DateTimeField(verbose_name='Дата публикации',
                                    auto_now_add=True, db_index=True)
    review = models.ForeignKey(Review, verbose_name='Отзыв',
                               related_name='comments',
                               on_delete=models.CASCADE)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
