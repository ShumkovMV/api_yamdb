from django.contrib.auth.models import AbstractUser
from django.db import models


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
        max_length=150,
        unique=True,
        verbose_name='Электронная почта')

    bio = models.TextField(
        max_length=2000,
        blank=True,
        null=True,
        verbose_name='Биография')

    role = models.CharField(
        max_length=10,
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

    def __str__(self):
        return self.username
