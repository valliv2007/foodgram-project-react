from django.contrib.auth.models import AbstractUser
from django.db import models


class User (AbstractUser):
    """Модель прользователей"""
    email = models.EmailField('E-mail', unique=True, blank=False)
    first_name = models.CharField('First_name', blank=False, max_length=150)
    last_name = models.CharField('Last_name', blank=False, max_length=150)
