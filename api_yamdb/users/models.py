import re
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from .constants import (
    BIO_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    ROLE_MAX_LENGTH
)


class CustomUser(AbstractUser):

    MODERATOR = 'moderator'
    ADMIN = 'admin'
    USER = 'user'

    ROLE = [
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
        (USER, 'user')
    ]

    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        verbose_name='Электронная почта')

    bio = models.TextField(
        max_length=BIO_MAX_LENGTH,
        blank=True,
        null=True,
        verbose_name='Биография')

    role = models.CharField(
        max_length=ROLE_MAX_LENGTH,
        choices=ROLE,
        default=USER,
        verbose_name='Роль'
    )

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_user(self):
        return self.role == self.USER

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_user_permissions',
        blank=True,
    )

    @property
    def post_count(self):
        return self.posts.count()

    def __str__(self):
        return self.username

    def clean(self):
        if not re.match(r'^[a-zA-Z0-9_]+$', self.username):
            raise ValidationError(
                'Имя пользователя может содержать только буквы,'
                'цифры и знаки подчеркивания.'
            )

        # Запрет на использование имени 'me'
        if self.username.lower() == 'me':
            raise ValidationError('Имя пользователя не может быть "me".')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
