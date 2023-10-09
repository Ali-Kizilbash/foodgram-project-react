from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        max_length=settings.USERNAME_MAX_LENGTH,
        verbose_name='Юзернейм',
        help_text='Юзернейм',
        unique=True,
    )
    first_name = models.CharField(
        max_length=settings.FIRST_NAME_MAX_LENGTH,
        verbose_name='Имя',
        help_text='Имя',
        blank=False,
    )
    last_name = models.CharField(
        max_length=settings.LAST_NAME_MAX_LENGTH,
        verbose_name='Фамилия',
        help_text='Фамилия',
        blank=False,
    )
    email = models.EmailField(
        max_length=settings.EMAIL_MAX_LENGTH,
        verbose_name='Эл. почта',
        help_text='Эл. почта',
        unique=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Тот, кто подписывается',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Тот, на кого подписываются',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='subscription'
            ),
        )

    def __str__(self):
        return f'{self.user} ::: {self.author}'
