from django.contrib.auth.models import AbstractUser
from django.db import models

ADMINISTRATOR = 'administrator'
USER = 'user'
GUEST = 'guest'
CHOICES = (
    (ADMINISTRATOR, 'Администратор'),
    (USER, 'Авторизованный пользователь'),
    (GUEST, 'Гость (неавторизованный пользователь)'),
)


class Subscription(models.Model):
    user = models.ForeignKey(
        'User',
        verbose_name='Пользователи',
        on_delete=models.CASCADE,
        related_name='subscribers',
    )
    subscriber = models.ForeignKey(
        'User',
        verbose_name='Подписчики',
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class User(AbstractUser):
    email = models.EmailField(
        'Адрес эл.почты',
        max_length=254,
    )
    role = models.CharField(
        'Роль пользователя',
        max_length=13,
        choices=CHOICES,
        default='user',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = (
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user'
            ),
        )
