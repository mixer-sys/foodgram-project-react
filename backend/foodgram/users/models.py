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
        on_delete=models.CASCADE,
        related_name='subscribers',
        blank=True
    )
    subscriber = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        blank=True
    )


class User(AbstractUser):

    email = models.EmailField(
        'Адрес эл.почты',
        max_length=254,
        blank=True
    )
    role = models.CharField(
        'Роль пользователя',
        max_length=13,
        choices=CHOICES,
        blank=True,
        null=True,
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
