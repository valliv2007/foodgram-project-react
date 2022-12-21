from django.contrib.auth.models import AbstractUser
from django.db import models


class User (AbstractUser):
    """Модель прользователей"""
    email = models.EmailField('E-mail', unique=True, blank=False)
    first_name = models.CharField('First_name', blank=False, max_length=150)
    last_name = models.CharField('Last_name', blank=False, max_length=150)


class Subscription(models.Model):
    """Модель подписок"""
    user = models.ForeignKey(User,
                             related_name="subscriber",
                             on_delete=models.CASCADE,
                             verbose_name="Subscriber")
    author = models.ForeignKey(User,
                               related_name="content_maker",
                               on_delete=models.CASCADE,
                               verbose_name="Content_maker")

    def __str__(self):
        return f'{self.user} subscribed {self.author}'

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        constraints = [models.UniqueConstraint(fields=['user', 'author'],
                       name='unique_subscribe')]
